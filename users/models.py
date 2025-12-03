from django.db import models

# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from tenants.models import Tenant
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="customer")
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="users", null=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.username} ({self.role})"
