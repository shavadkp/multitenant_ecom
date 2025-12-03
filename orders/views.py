from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins
from .models import Order
from .serializers import OrderSerializer, PlaceOrderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None) or getattr(self.request.user, "tenant", None)
        user = self.request.user
        if user.role in ("owner", "staff"):
            return Order.objects.filter(tenant=tenant)
        return Order.objects.filter(tenant=tenant, customer=user)

    @action(detail=False, methods=["post"], url_path="", url_name="place_order")
    def place_order(self, request):
        serializer = PlaceOrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        out = OrderSerializer(order, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)
