from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        # Admin a accès à tout
        if request.user.is_superuser:
            return True
        
        # Sinon, un farmer n'a accès qu'à son propre objet
        return obj.owner == request.user
