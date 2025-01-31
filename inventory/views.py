# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from .permissions import IsCompanyMember, IsCompanyMemberOrCreate

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        return Product.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        return Sale.objects.filter(company=self.request.user.company)
    
    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

# Similar ViewSets for other models (Purchase, ProductionOrder, etc.)
class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)
    
    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['receipt_number', 'total']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase = Purchase.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            item = PurchaseItem.objects.create(purchase=purchase, **item_data)
            total += item.price * item.quantity
            item.product.stock += item.quantity * item.unit.conversion_factor
            item.product.save()
        purchase.total = total
        purchase.save()
        return purchase

class ProductionOrderSerializer(serializers.ModelSerializer):
    inputs = ProductionInputSerializer(many=True)
    
    class Meta:
        model = ProductionOrder
        fields = '__all__'

    def create(self, validated_data):
        inputs_data = validated_data.pop('inputs')
        order = ProductionOrder.objects.create(**validated_data)
        for input_data in inputs_data:
            ProductionInput.objects.create(production_order=order, **input_data)
            # Handle inventory updates here
        return order
    
class PurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsCompanyMemberOrCreate, IsCompanyMember]

    def get_queryset(self):
        return Purchase.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

class ProductionOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ProductionOrderSerializer
    permission_classes = [IsCompanyMemberOrCreate, IsCompanyMember]

    def get_queryset(self):
        return ProductionOrder.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

class VendorViewSet(viewsets.ModelViewSet):
    serializer_class = VendorSerializer
    permission_classes = [IsCompanyMemberOrCreate, IsCompanyMember]

    def get_queryset(self):
        return Vendor.objects.filter(company=self.request.user.company)

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsCompanyMemberOrCreate, IsCompanyMember]

    def get_queryset(self):
        return Client.objects.filter(company=self.request.user.company)

class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [IsCompanyMemberOrCreate, IsCompanyMember]

    def get_queryset(self):
        return Unit.objects.filter(company=self.request.user.company)