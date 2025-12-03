from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from django.db import transaction
from decimal import Decimal

class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    qty = serializers.IntegerField(min_value=1)

class PlaceOrderSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)

    def validate(self, data):
        request = self.context["request"]
        tenant = getattr(request, "tenant", request.user.tenant)
        product_ids = [item["product_id"] for item in data["items"]]
        products = Product.objects.filter(id__in=product_ids, tenant=tenant)
        if products.count() != len(set(product_ids)):
            raise serializers.ValidationError("One or more products not found in tenant")
        # check stock
        prod_map = {p.id: p for p in products}
        for it in data["items"]:
            p = prod_map.get(it["product_id"])
            if p.stock < it["qty"]:
                raise serializers.ValidationError(f"Insufficient stock for product {p.name}")
        return data

    def create(self, validated_data):
        request = self.context["request"]
        tenant = getattr(request, "tenant", request.user.tenant)
        user = request.user
        items = validated_data["items"]

        with transaction.atomic():
            order = Order.objects.create(tenant=tenant, customer=user, status="pending", total_amount=0)
            total = Decimal("0")
            for it in items:
                product = Product.objects.select_for_update().get(id=it["product_id"], tenant=tenant)
                quantity = it["qty"]
                if product.stock < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}")

                product.stock -= quantity
                product.save()

                item_price = product.price
                OrderItem.objects.create(order=order, product=product, quantity=quantity, price=item_price)
                total += (item_price * quantity)

            order.total_amount = total
            order.save()
        return order

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id","tenant","customer","total_amount","status","created_at","items"]

    def get_items(self, obj):
        return [
            {"product": item.product.name, "quantity": item.quantity, "price": item.price}
            for item in obj.items.all()
        ]
