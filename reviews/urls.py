from django.urls import path
from reviews.views import UserAPIView, UserDetailAPIView, ReviewAPIView, ReviewDetailAPIView, CompanyAPIView, CompanyDetailAPIView, CategoryAPIView, CategoryDetailAPIView

api_patterns = [
    path('users/', UserAPIView.as_view(), name='users-list'),
    path('users/<int:id>/', UserDetailAPIView.as_view(), name='users-detail'),
    path('reviews/', ReviewAPIView.as_view(), name='reviews-list'),
    path('reviews/<int:id>/', ReviewDetailAPIView.as_view(), name='reviews-detail'),
    path('companies/', CompanyAPIView.as_view(), name='companies-list'),
    path('companies/<int:id>/', CompanyDetailAPIView.as_view(), name='companies-detail'),
    path('categories/', CategoryAPIView.as_view(), name='categories-list'),
    path('categories/<int:id>/', CategoryDetailAPIView.as_view(), name='categories-detail'),
]