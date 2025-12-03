# users/serializers.py
from rest_framework import serializers
from .models import User
from tenants.models import Tenant
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    store_name = serializers.CharField()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        store_name = validated_data.pop("store_name")
        tenant = Tenant.objects.create(store_name=store_name, contact_email=validated_data["email"])
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role="owner",
            tenant=tenant,
            is_active=True
        )
        return {"user": user, "tenant": tenant}
