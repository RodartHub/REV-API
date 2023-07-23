from rest_framework.serializers import ModelSerializer, SerializerMethodField
from reviews.models import UserModel, ReviewModel, CompanyModel, CategoryModel

class UserSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        # fields = ['id', 'name', 'lastname', 'username', 'email', 'phone', 'image', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        fields = '__all__'

class ReviewSerializer(ModelSerializer):
    user = SerializerMethodField()
    company = SerializerMethodField()
    class Meta:
        model = ReviewModel
        fields = ['id', 'description', 'user', 'rating', 'company', 'created_at', 'updated_at']

    def get_user(self, obj):
        user = obj.user
        image_path = user.image
        return {'id': user.id, 'username': user.name, 'image': image_path}
    
    def get_company(self, obj):
        company = obj.company
        return {'id': company.id, 'name': company.name}
    
    
class CompanySerializer(ModelSerializer):
    category = SerializerMethodField()
    reviews = SerializerMethodField()
    rating = SerializerMethodField()
    reviews_count = SerializerMethodField()
    class Meta:
        model = CompanyModel
        # fields = ['id', 'name', 'address', 'phone', 'email', 'category', 'reviews', 'image', 'city', 'created_at', 'updated_at', 'password']
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def get_category(self, obj):
        category = obj.category
        return {'id': category.id, 'name': category.name}
    
    def get_reviews(self, obj):
        reviews = obj.reviews.all()  # Obtén todas las reviews de la compañía actual
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data
    
    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            average_rating = round(total_rating / len(reviews))
            return average_rating
        return 0

    def get_reviews_count(self, obj):
        reviews = obj.reviews.all()
        return len(reviews)

class CategorySerializer(ModelSerializer):
    companies = SerializerMethodField()
    class Meta:
        model = CategoryModel
        # fields = ['id', 'name', 'companies', 'created_at', 'updated_at']
        fields = '__all__'

    def get_companies(self, obj):
        companies = obj.companies.all()
        return [{'id': company.id, 'name': company.name} for company in companies]
    