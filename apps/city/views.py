from apps.common.views.api import AppModelCUDAPIViewSet, AppModelListAPIViewSet, AppAPIView
from apps.city.models import City
from apps.city.serializer import CityCUDSerializer, CityListSerializer
from apps.common.views.api import export_common_csv

class CityCUDAPIViewSet(AppModelCUDAPIViewSet):
    """
    View to handle `City` creation, update and delete.
    """

    queryset = City.objects.all()
    serializer_class = CityCUDSerializer


class CityListAPIViewSet(AppModelListAPIViewSet):
    """List API view for City"""

    serializer_class = CityListSerializer
    queryset = City.objects.all().order_by("is_deleted", "-created_at")
    filterset_fields = ["is_deleted"]

    all_table_columns = {
        "name": "City Name",
    }

    def get_meta_for_table(self) -> dict:
        data = {
            "columns": self.get_table_columns(),
        }
        return data
    
class CityExportAPIView(AppAPIView):
    """
    The CityExportAPIView.This view will export cities to excel.
    """

    queryset = City.objects.all()

    def get(self, request, *args, **kwargs):
        """On get, download the file."""

        return export_common_csv(request, ["id", "name"], model=City)