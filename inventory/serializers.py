# serializers.py
from rest_framework import serializers
from .models import *

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    base_unit = UnitSerializer(read_only=True)
    allowed_units = UnitSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['company', 'sku', 'stock']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    
    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ['invoice_number', 'total']

class ProductionInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionInput
        fields = '__all__'

class ProductionOrderSerializer(serializers.ModelSerializer):
    inputs = ProductionInputSerializer(many=True)
    
    class Meta:
        model = ProductionOrder
        fields = '__all__'

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