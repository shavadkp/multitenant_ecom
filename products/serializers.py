from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id","tenant","name","sku","description","price","stock","created_at"]
        read_only_fields = ["id", "tenant", "created_at"]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        # enforce tenant from request
        validated_data["tenant"] = getattr(request, "tenant", request.user.tenant)
        return super().create(validated_data)
