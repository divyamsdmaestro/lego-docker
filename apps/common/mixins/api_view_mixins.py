import contextlib
from contextlib import suppress

from rest_framework import permissions, status
from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.status import is_success

from apps.common.config import API_RESPONSE_ACTION_CODES


class NonAuthenticatedAPIMixin:
    """
    The mixin class which defines an API class as non-authenticated.
    The users can access this api without login. Just DRY stuff.
    """

    permission_classes = [permissions.AllowAny]


class AppViewMixin:
    """
    The base view class for all the application view. Contains common methods
    and overrides to main integrity and schema.
    """

    get_object_model = None

    def get_request(self):
        """Returns the request."""

        return self.request

    def get_user(self):
        """Returns the current user."""

        return self.get_request().user

    def get_authenticated_user(self):
        """Returns the authenticated user."""

        user = self.get_user()
        return user if user and user.is_authenticated else None

    def get_object(self):
        """
        Suppose you want to list data based on an other model. This
        is a centralized function to do the same.
        """

        lookup_kwargs = {"pk": self.kwargs.get("pk")}
        if self.get_object_model:
            with contextlib.suppress(AttributeError):
                lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
                if self.lookup_field and self.kwargs.get(lookup_url_kwarg):
                    lookup_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            if _object := self.get_object_model.objects.get_or_none(**lookup_kwargs):
                return _object
            else:
                raise NotFound

        return super().get_object()

    def send_error_response(self, data=None):
        """Central function to send error response."""

        return self.send_response(data=data, status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_response(data=None, status_code=status.HTTP_200_OK, action_code="DO_NOTHING", **other_response_data):
        """Custom function to send the centralized response."""

        return Response(
            data={
                "data": data,
                "status": "success" if is_success(status_code) else "error",
                "action_code": action_code,  # make the FE do things based on this
                **other_response_data,
            },
            status=status_code,
        )

    def get_app_response_schema(self, response: Response, **kwargs):
        """Given a drf response object. This converts it to the application schema."""

        return self.send_response(data=response.data, status_code=response.status_code, **kwargs)

    def handle_exception(self, exc):
        """Overridden to maintain applications response schema."""

        # pre-process action code
        action_code = API_RESPONSE_ACTION_CODES["display_error_1"]
        if exc and hasattr(exc, "status_code") and exc.status_code in [401]:
            action_code = "AUTH_TOKEN_NOT_PROVIDED_OR_INVALID"

        return self.get_app_response_schema(super().handle_exception(exc), action_code=action_code)

    def list(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().list(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def retrieve(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().retrieve(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def create(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().create(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def update(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().update(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def destroy(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().destroy(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def partial_update(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().partial_update(request, *args, **kwargs))

        raise MethodNotAllowed(method=self.get_request().method)


class SortingMixin:
    """
    A mixin class for adding sorting functionality to API views.
    """

    def get_queryset(self):
        """Overridden to sort the queryset based on the query parameters passed."""

        return self.get_sorted_queryset()

    def get_sorted_queryset(self):
        """
        Return a sorted queryset based on the 'sort_by' query parameter.
        """

        queryset = super().get_queryset()
        if sort_by := self.request.query_params.get("sort_by"):
            try:
                queryset = queryset.order_by(sort_by)
            except Exception:
                raise ValidationError("Invalid field name for sorting.")
        return queryset

    def get_default_sorting_options(self):
        """
        Return the default sorting options as a dictionary of option IDs and labels.
        """

        return {
            "name": "A to Z",
            "-name": "Z to A",
        }
    
    def get_sorting_meta(self, sorting_options: dict):
        """Return value and corresponding label for sorting the list."""

        return [{"id": key, "identity": value} for key, value in sorting_options.items()]

    def get_sorting_options(self, specific_options={}):
        """
        Return the sorting options with specific additional options as a dictionary of option IDs and labels.
        """

        options = self.get_default_sorting_options().copy()
        options.update(specific_options)
        return self.get_sorting_meta(options)
    
class AbstractLookUpFieldMixin:
    """
    This class provides config for which field to look in the model as well as
    in url.
    """

    lookup_url_kwarg = "uuid"
    lookup_field = "uuid"
