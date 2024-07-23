from django.urls import path
from rest_framework.routers import SimpleRouter
from apps.access.social_login import SocialLoginAPIView, SocialCallbackAPIView


app_name = "access"
API_URL_PREFIX = "api/access/"

router = SimpleRouter()

urlpatterns = [
    path("<str:provider>/login/", SocialLoginAPIView.as_view()),
    path("<str:provider>/callback/", SocialCallbackAPIView.as_view()),
]
