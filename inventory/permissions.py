from rest_framework import permissions

class IsCompanyMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.company == request.user.company

class IsCompanyMemberOrCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.company is not None
        return True