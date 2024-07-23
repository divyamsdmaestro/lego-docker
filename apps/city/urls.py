from apps.common.routers import AppSimpleRouter
from apps.city.views import CityCUDAPIViewSet, CityListAPIViewSet, CityExportAPIView
from apps.common.views.api import ArchiveAPIView
from django.urls import path

router = AppSimpleRouter()

router.register("city-cud", CityCUDAPIViewSet, basename="city-cud")
router.register("city-list", CityListAPIViewSet, basename="city-list")

urlpatterns = [] + router.urls

# Add the ArchiveAPIView directly to urlpatterns
urlpatterns += [
    path('city-archive/', ArchiveAPIView.as_view(), name='city-archive'),
    path('city-export/', CityExportAPIView.as_view(), name='city-export'),
]