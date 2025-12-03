# core/middleware.py
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

class TenantMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Try to get tenant from JWT first
        try:
            user_auth_tuple = JWTAuthentication().authenticate(request)
            if user_auth_tuple is not None:
                user, token = user_auth_tuple
                tenant_id = token.get("tenant_id", None)
                if tenant_id:
                    from tenants.models import Tenant
                    try:
                        request.tenant = Tenant.objects.get(id=tenant_id)
                    except Tenant.DoesNotExist:
                        request.tenant = None
                request.user = user
                return
        except Exception:
            # fail silently and try header
            request.tenant = None

        # fallback to header X-TENANT-ID
        tenant_header = request.headers.get("X-TENANT-ID")
        if tenant_header:
            from tenants.models import Tenant
            try:
                request.tenant = Tenant.objects.get(id=tenant_header)
            except Tenant.DoesNotExist:
                request.tenant = None
        else:
            request.tenant = None
