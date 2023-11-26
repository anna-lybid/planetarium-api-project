from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class CanCreateAndRead(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS and request.user.is_authenticated:
            return True
        if request.method == "POST":
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return False
