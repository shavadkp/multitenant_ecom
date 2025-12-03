# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSameTenant(BasePermission):
    """
    Ensure object belongs to the same tenant as request.user / request.tenant
    """
    def has_object_permission(self, request, view, obj):
        tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
        obj_tenant = getattr(obj, "tenant", None)
        return tenant and obj_tenant and str(tenant.id) == str(obj_tenant.id)

    def has_permission(self, request, view):
        return True

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "owner"

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "staff"

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "customer"
