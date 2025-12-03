from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsOwner, IsStaff, IsSameTenant
from rest_framework.response import Response
from rest_framework import status

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsSameTenant]  # object-level
    lookup_field = "id"

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None) or getattr(self.request.user, "tenant", None)
        return Product.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        # Additional role checks
        user_role = getattr(self.request.user, "role", None)
        if user_role not in ("owner", "staff"):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only owner or staff can create products")
        serializer.save()
