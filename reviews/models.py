from django.db import models

# ------------------- USERS ------------------- 
class UserModel(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=255, unique=True)
    image = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            db_table = "users"
            ordering = ['-created_at']

# ------------------- CATEGORY -------------------

class CategoryModel(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            db_table = "categories"
            ordering = ['-created_at']

# ------------------- COMPANY ------------------- 

class CompanyModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    uid = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    image = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, related_name='companies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            db_table = "companies"
            ordering = ['-created_at']


# ------------------- REVIEWS ------------------- 
class ReviewModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reviews')
    description = models.TextField()
    rating = models.IntegerField()
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
            db_table = "reviews"
            ordering = ['-created_at']
    
