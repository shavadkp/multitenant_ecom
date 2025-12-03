# users/tokens.py
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    # add custom claims
    refresh["tenant_id"] = str(user.tenant.id) if user.tenant else None
    refresh["role"] = user.role
    refresh["username"] = user.username
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
