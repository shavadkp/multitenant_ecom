from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .tokens import get_tokens_for_user
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = []  # allow any

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result["user"]
        tenant = result["tenant"]
        tokens = get_tokens_for_user(user)
        return Response({
            "user": {"id": str(user.id), "username": user.username, "role": user.role},
            "tenant": {"id": str(tenant.id), "store_name": tenant.store_name},
            **tokens
        }, status=status.HTTP_201_CREATED)

# Custom Token serializer to include claims in access token (though get_tokens_for_user already adds)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["tenant_id"] = str(user.tenant.id) if user.tenant else None
        token["role"] = user.role
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
