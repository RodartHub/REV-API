from rest_framework import status
from rest_framework.views import APIView 
from rest_framework.response import Response
from reviews.models import UserModel, ReviewModel, CompanyModel, CategoryModel
from reviews.serializers import UserSerializer, ReviewSerializer, CompanySerializer, CategorySerializer
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import NotFound
from django.db.models import Count, Q, Avg, IntegerField
from django.db.models.functions import Cast, Round

# ------------------- USERS ------------------- 
class UserAPIView(APIView):

    def get(self, request):
        users = UserModel.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = {
            'uid': request.data.get('uid'),
            'name': request.data.get('name'),
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'image': request.data.get('image')
        }
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data['password'])
            serializer.validated_data['password'] = password
            serializer.save()
            return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAPIView(APIView):

    def get_object(self, id):
        try:
            return UserModel.objects.get(pk=id)
        except UserModel.DoesNotExist:
            return None
    
    def get(self, request, id):
        user = self.get_object(id)
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        reviews = user.reviews.all()
        reviews_serializer = ReviewSerializer(reviews, many=True)
        user_serializer = UserSerializer(user)
        response_data = {
            "user": user_serializer.data,
            "reviews": reviews_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = self.get_object(id)
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            if 'password' in serializer.validated_data:
                # Encriptar la nueva contraseña
                password = make_password(serializer.validated_data['password'])
                serializer.validated_data['password'] = password

            serializer.save()
            return Response({"message": "User updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        user = self.get_object(id)
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"message": "User deleted"}, status=status.HTTP_200_OK)
    
# ------------------- REVIEWS -------------------

class ReviewAPIView(APIView):

    def get(self, request):
        reviews = ReviewModel.objects.all().select_related('user')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user_id = request.data.get('user_id')
        user = UserModel.objects.get(id=user_id)

        company_id = request.data.get('company_id')
        company = CompanyModel.objects.get(id=company_id)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, company=company)
            return Response({"message": "Review created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailAPIView(APIView):

    def get_object(self, id):
        try:
            return ReviewModel.objects.get(pk=id)
        except ReviewModel.DoesNotExist:
            return None
    
    def get(self, request, id):
        review = self.get_object(id)
        if not review:
            return Response({"message": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        review = self.get_object(id)
        if not review:
            return Response({"message": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Review updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        review = self.get_object(id)
        if not review:
            return Response({"message": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response({"message": "Review deleted"}, status=status.HTTP_200_OK)


# ------------------- COMPANIES -------------------

class CompanyAPIView(APIView):

    def get(self, request):
        query_params = request.GET.dict()

        # Filtrar los parámetros de la consulta
        category_id = query_params.get('category_id')
        rating = query_params.get('rating')
        order_by = query_params.get('order_by')
        search_query = query_params.get('name') 

        # Obtener las compañías sin filtros iniciales
        companies = CompanyModel.objects.all().select_related('category')

        # Obtener el promedio de rating y el número de reviews de cada compañía
        companies = self.calculate_average_rating_and_reviews_count(companies)

        # Filtrar por consulta de búsqueda si se proporciona
        if search_query:
            companies = companies.filter(Q(name__icontains=search_query))

        # Aplicar filtros adicionales según los parámetros de la consulta
        if category_id or rating:
            companies = self.apply_filters(companies, category_id, rating)

        # Aplicar ordenamiento según la opción seleccionada
        if order_by == '1':
            companies = companies.order_by('-reviews_count')
        elif order_by == '2':
            companies = companies.order_by('reviews_count')

        if not companies.exists():
            raise NotFound("No se encontraron compañías que cumplan con los filtros especificados.")

        serializer = CompanySerializer(companies, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def calculate_average_rating_and_reviews_count(self, companies):
        # Obtener el promedio de rating y el número de reviews de cada compañía
        companies = companies.annotate(average_rating=Cast(Round(Avg('reviews__rating')), output_field=IntegerField()))
        companies = companies.annotate(reviews_count=Count('reviews'))
        
        return companies

    def apply_filters(self, companies, category_id, rating):
        # Aplicar filtros según los parámetros proporcionados
        set_companies = companies

        filters = Q()

        if category_id:
            filters &= Q(category__id=category_id)

        if rating:
            rating = int(rating)
            filters &= Q(average_rating__exact=rating)  
        # Filtrar las compañías según los filtros definidos
        filtered_companies = set_companies.filter(filters)

        return filtered_companies
    
    def post(self, request):
        data = {
            'name': request.data.get('name'),
            'uid': request.data.get('uid'),
            'address': request.data.get('address'),
            'phone': request.data.get('phone'),
            'category_id': request.data.get('category'),  # 'category_id' es el nombre del campo en el frontend
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'image': request.data.get('image')
        }
        
        category_id = data['category_id']
        category = CategoryModel.objects.get(id=category_id)
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            password = make_password(serializer.validated_data['password'])
            serializer.validated_data['password'] = password
            serializer.save(category=category)
            companies = CompanyModel.objects.all()  # Obtener todos los registros del modelo
            company_serializer = CompanySerializer(companies, many=True) 
            
            return Response(company_serializer.data, status=status.HTTP_201_CREATED)
        else:
            (serializer.errors)  # Imprimir los errores en la consola para su revisión
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CompanyDetailAPIView(APIView):

    def get_object(self, id):
        try:
            return CompanyModel.objects.get(pk=id)
        except CompanyModel.DoesNotExist:
            return None
    
    def get(self, request, id):
        company = self.get_object(id)
        if not company:
            return Response({"message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        company = self.get_object(id)
        if not company:
            return Response({"message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            if 'password' in serializer.validated_data:
                # Encriptar la nueva contraseña
                password = make_password(serializer.validated_data['password'])
                serializer.validated_data['password'] = password

            serializer.save()
            return Response({"message": "Company updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        company = self.get_object(id)
        if not company:
            return Response({"message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        company.delete()
        return Response({"message": "Company deleted"}, status=status.HTTP_200_OK)


# ------------------- CATEGORIES -------------------

class CategoryAPIView(APIView):

    def get(self, request):
        categories = CategoryModel.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryDetailAPIView(APIView):
    def get_object(self, id):
        try:
            return CategoryModel.objects.get(pk=id)
        except CategoryModel.DoesNotExist:
            return None
    
    def get(self, request, id):
        category = self.get_object(id)
        if not category:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        category = self.get_object(id)
        if not category:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        category = self.get_object(id)
        if not category:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response({"message": "Category deleted"}, status=status.HTTP_200_OK)
    





