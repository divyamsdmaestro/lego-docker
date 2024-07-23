import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet

from apps.common.helpers import custom_capitalize
from apps.common.pagination import AppPagination
from apps.common.views.api.base import AppViewMixin

logger = logging.getLogger(__name__)


class AppGenericViewSet(GenericViewSet):
    """
    Applications version of the `GenericViewSet`. Overridden to implement
    app's necessary features. Also used in the CRUD viewsets.

    Note:
        1. An APIView is different from an APIViewSet.
        2. An APIView is registered using:
            path("url/endpoint/", APIView.as_view())
        3. An APIViewSet is registered using:
            router.register(
                "url/endpoint",
                APIViewSet,
                basename="base_name_if_needed",
            )

    Why is this implemented?
        > Consider an Update API that has to be implemented.
        > The API has to send the following:
            >> Initial data (ids).
            >> Metadata for select options.
            >> Handle the update operations.
        > If implemented using APIView, there has to be at least 2 view classes.
        > If implemented using APIViewSet, it is only one view.
        > Hence reduces the development time.
    """

    policy_slug = None


class AppModelListAPIViewSet(
    AppViewMixin,
    ListModelMixin,
    AppGenericViewSet,
):
    """
    Applications base list APIViewSet. Handles all the listing views.
    This also sends the necessary filter meta and table config data.

    Also handles listing operations like sort, search, filter and
    table preferences of the user.

    References:
        1. https://github.com/miki725/django-url-filter
        2. https://www.django-rest-framework.org/api-guide/filtering/
    """

    pagination_class = AppPagination  # page-size: 25
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = []  # override
    search_fields = []  # override
    ordering_fields = "__all__"
    all_table_columns = {}

    @action(
        methods=["GET"],
        url_path="table-meta",
        detail=False,
    )
    def get_meta_for_table_handler(self, *args, **kwargs):
        """
        Sends out all the necessary config for the front-end table. The
        config can vary based on user permission and preference.
        """

        serializer = self.get_serializer_class()
        if not self.all_table_columns:
            table_meta = {field: custom_capitalize(field) for field in serializer.Meta.fields}
        else:
            table_meta = self.all_table_columns
        return self.send_response(data={"columns": table_meta})


class AppModelRetrieveAPIViewSet(
    AppViewMixin,
    RetrieveModelMixin,
    AppGenericViewSet,
):
    """App version of RetrieveModelViewSet."""

    def retrieve(self, request, *args, **kwargs):
        """Overriden to include logs."""

        model_name = self.get_object().__class__.__name__
        logger.debug(f"Retrieving a {model_name} object with id: {kwargs['pk']} by {self.get_user()}")
        return super().retrieve(request, *args, **kwargs)


class AppModelCUDAPIViewSet(
    AppViewMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    AppGenericViewSet,
):
    """
    What is CUD?
        Create, Update & Delete

    What is a CUD ViewSet?
        A ViewSet that handles the necessary CUD operations.

    Why is this separated from the ModelViewSet?
        User Permissions can be two types:
            > View
            > Modify
        An user can have anyone or both for a particular entity like `ProjectType`.
        These conditions can be handled easily, when the CUD is separated.

    Urls Allowed:
        > POST: {endpoint}/
            >> Get data from front-end and creates an object.
        > GET: {endpoint}/meta/
            >> Returns metadata for the front-end for object creation.

        > PUT: {endpoint}/<pk>/
            >> Get data from font-end to update an object.
        > GET: {endpoint}/<pk>/meta/
            >> Returns metadata for the front-end for object update.

        > DELETE: {endpoint}/<pk>/
            >> Deletes the object identified by the passed `pk`.
    """

    def create(self, request, *args, **kwargs):
        """Overriden to include logs."""

        model_name = self.get_serializer_class().Meta.model.__name__
        logger.debug(f"Creating a {model_name} object with data: {request.data} by {self.get_user()}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Overriden to include logs."""

        model_name = self.get_object().__class__.__name__
        logger.debug(f"Updating a {model_name} object with id: {kwargs['pk']} by {self.get_user()}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Overriden to include logs and deleted_by."""

        model_name = self.get_object().__class__.__name__
        logger.debug(f"Deleting a {model_name} object with id: {kwargs['pk']} by {self.get_user()}")
        instance = self.get_object()
        self.perform_destroy(instance)
        if hasattr(instance, "deleted_by"):
            instance.deleted_by = self.get_user()
            instance.save()
        return self.send_response()

    @action(
        methods=["GET"],
        url_path="meta",
        detail=False,
    )
    def get_meta_for_create(self, *args, **kwargs):
        """Returns the meta details for create from serializer."""

        return self.send_response(data=self.get_serializer().get_meta_for_create())

    @action(
        methods=["GET"],
        url_path="meta",
        detail=True,
    )
    def get_meta_for_update(self, *args, **kwargs):
        """Returns the meta details for update from serializer."""

        return self.send_response(data=self.get_serializer(instance=self.get_object()).get_meta_for_update())


class AppModelCreateAPIViewSet(
    AppViewMixin,
    CreateModelMixin,
    AppGenericViewSet,
):
    """
    Urls Allowed:
        > POST: {endpoint}/
            >> Get data from front-end and creates an object.
        > GET: {endpoint}/meta/
            >> Returns metadata for the front-end for object creation.
    """

    def create(self, request, *args, **kwargs):
        """Overriden to include logs."""

        model_name = self.get_serializer_class().Meta.model.__name__
        logger.debug(f"Creating a {model_name} object with data: {request.data} by {self.get_user()}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Not allowed."""

        return NotImplementedError

    def destroy(self, request, *args, **kwargs):
        """Not allowed."""

        return NotImplementedError

    @action(
        methods=["GET"],
        url_path="meta",
        detail=False,
    )
    def get_meta_for_create(self, *args, **kwargs):
        """Returns the meta details for create from serializer."""

        return self.send_response(data=self.get_serializer().get_meta_for_create())


class AppModelUpdateAPIViewSet(
    AppViewMixin,
    UpdateModelMixin,
    AppGenericViewSet,
):
    """
    Urls Allowed:
        > PUT: {endpoint}/<pk>/
            >> Get data from font-end to update an object.
        > GET: {endpoint}/<pk>/meta/
            >> Returns metadata for the front-end for object update.

    """

    def create(self, request, *args, **kwargs):
        """Not Supported."""

        return NotImplementedError

    def update(self, request, *args, **kwargs):
        """Overriden to include logs."""

        model_name = self.get_object().__class__.__name__
        logger.debug(f"Updating a {model_name} object with id: {kwargs['pk']} by {self.get_user()}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Not supported."""

        return NotImplementedError

    @action(
        methods=["GET"],
        url_path="meta",
        detail=True,
    )
    def get_meta_for_update(self, *args, **kwargs):
        """Returns the meta details for update from serializer."""

        return self.send_response(data=self.get_serializer(instance=self.get_object()).get_meta_for_update())