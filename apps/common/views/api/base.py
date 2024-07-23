
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from apps.common.mixins import AppViewMixin
from apps.common.serializers import AppModelSerializer
from rest_framework import parsers


class AppAPIView(AppViewMixin, APIView):
    """
    Common api view class for the entire application. Just a central view to customize
    the output response schema. The entire application will follow this schema.
    """

    get_object_model = None
    serializer_class = None
    policy_slug = None

    def get_valid_serializer(self, instance=None):
        """Central function to get the valid serializer. Raises exceptions."""

        assert self.serializer_class

        # pylint: disable=not-callable
        serializer = self.serializer_class(
            data=self.request.data,
            context=self.get_serializer_context(),
            instance=instance,
        )
        serializer.is_valid(raise_exception=True)
        return serializer

    def get_serializer_context(self):
        """Central function to pass the serializer context."""

        return {"request": self.get_request()}

    def get_object(self, exception=NotFound, identifier="pk"):
        """
        Suppose you want to list data based on an other model. This
        is a centralized function to do the same.
        """

        if self.get_object_model:
            if _object := self.get_object_model.objects.get_or_none(**{identifier: self.kwargs[identifier]}):
                return _object

            else:
                raise exception

        return super().get_object()


class AppCreateAPIView(AppViewMixin, CreateAPIView):
    """App's version on the `CreateAPIView`, implements custom handlers."""

    def perform_create(self, serializer):
        """Overridden to call the post create handler."""

        instance = serializer.save()
        self.perform_post_create(instance=instance)

    def perform_post_create(self, instance):
        """Called after `perform_create`. Handle custom logic here."""

        pass


def get_upload_api_view(meta_model, meta_fields=None):
    """Central function to return the UploadAPIView. Used to handle uploads."""

    if not meta_fields:
        meta_fields = ["file", "id"]

    class _View(AppCreateAPIView):
        """View to handle the upload."""

        class _Serializer(AppModelSerializer):
            """Serializer for write."""

            class Meta(AppModelSerializer.Meta):
                model = meta_model
                fields = meta_fields

        parser_classes = [parsers.MultiPartParser]
        serializer_class = _Serializer

    return _View
