from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from django.utils.timezone import now


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    phone_number_2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True,
        help_text="Company logo image"
    )

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    COMPANY_ROLES = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('STAFF', 'Regular Staff'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=COMPANY_ROLES, default='STAFF')
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Permission fixes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name="inventory_users",
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="inventory_users_perms",
        blank=True,
        help_text='Specific permissions for this user.',
    )

class Client(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True)
    phone_number_2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.company})"

class Vendor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    # Contact Information
    phone_number = models.CharField(max_length=20, blank=True )
    phone_number_2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.company})"

class Unit(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    base_unit = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='derived_units'
    )
    conversion_factor = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=1,
        help_text="Multiplier to convert to base unit"
    )

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    sku = models.UUIDField(default=uuid.uuid4, editable=False)
    description = models.TextField(blank=True)
    base_unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    stock = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    reorder_level = models.DecimalField(default=0, max_digits=15, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    allowed_units = models.ManyToManyField(Unit, related_name='allowed_products')

class ProductionOrder(models.Model):
    PRODUCTION_STATUS = (
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    production_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=PRODUCTION_STATUS, default='PLANNED')
    output_product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='productions')
    quantity_produced = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    good_quantity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    damaged_quantity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    notes = models.TextField(blank=True)

class ProductionInput(models.Model):
    QUALITY_STATUS = (
        ('GOOD', 'Good'),
        ('DAMAGED', 'Damaged'),
        ('EXCESS', 'Excess'),
        ('SHORT', 'Short')
    )
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='inputs')
    raw_material = models.ForeignKey(Product, on_delete=models.PROTECT)
    planned_quantity = models.DecimalField(max_digits=15, decimal_places=4, blank=True)
    actual_used = models.DecimalField(max_digits=15, decimal_places=4, blank=True)
    wastage = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    quality_status = models.CharField(max_length=20, choices=QUALITY_STATUS, default='GOOD')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)

class Sale(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    invoice_number = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=15, decimal_places=4,default=0)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)

class Purchase(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    receipt_number = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)