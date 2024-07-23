from apps.common.serializers import (
    AppReadOnlyModelSerializer,
    AppWriteOnlyModelSerializer,
)
from apps.city.models import City


class CityCUDSerializer(AppWriteOnlyModelSerializer):
    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = City
        fields = ["name"]
        extra_kwargs = {}

    def get_meta(self) -> dict:
        return {}

class CityListSerializer(AppReadOnlyModelSerializer):
    class Meta(AppReadOnlyModelSerializer.Meta):
        fields = [
            "id",
            "uuid",
            "name",
            "is_deleted",
        ]
        model = City