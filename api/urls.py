# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from inventory import views as inventory_views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'products', inventory_views.ProductViewSet, basename='product')
router.register(r'sales', inventory_views.SaleViewSet, basename='sale')
router.register(r'purchases', inventory_views.PurchaseViewSet, basename='purchase')
router.register(r'production', inventory_views.ProductionOrderViewSet, basename='production')
router.register(r'vendors', inventory_views.VendorViewSet, basename='vendor')
router.register(r'clients', inventory_views.ClientViewSet, basename='client')
router.register(r'units', inventory_views.UnitViewSet, basename='unit')

# Custom authentication endpoints
urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Inventory endpoints
    path('', include(router.urls)),
    
]