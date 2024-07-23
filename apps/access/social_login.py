import requests
from authlib.integrations.requests_client import OAuth2Session
from apps.access.config import UserLoginTypeChoices
from apps.common.views.api import AppAPIView
from apps.common.mixins import NonAuthenticatedAPIMixin
from config.settings import base


def get_oauth_details(provider):
    """Get OAuth details from settings."""

    oauth_settings = base.AUTHLIB_OAUTH_CLIENTS.get(provider, {})
    oauth = OAuth2Session(client_id=oauth_settings.get("client_id"), redirect_uri=oauth_settings.get("redirect_uri"))
    return oauth_settings, oauth


def get_user_data(provider, access_token, oauth_settings):
    """Get user data from Provider like google, fb, etc."""

    response = requests.get(oauth_settings.get("userinfo_url"), headers={"Authorization": f"Bearer {access_token}"})
    user_data = None
    if response.status_code == 200:
        response = response.json()
        if provider == UserLoginTypeChoices.google:
            user_data = {
                "first_name": response.get("given_name"),
                "last_name": response.get("family_name", None),
                "email": response.get("email"),
                "login_method": UserLoginTypeChoices.google,
            }
    return user_data


class SocialLoginAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Common APIView to generate link to login using Google, fb, etc."""

    def get(self, request, *args, **kwargs):
        """Generate authentication link to login social account with client_id."""

        provider = kwargs["provider"]
        oauth_settings, oauth = get_oauth_details(provider)
        authorization_url, _ = oauth.create_authorization_url(
            oauth_settings.get("authorize_url"), scope=oauth_settings.get("client_kwargs", {}).get("scope", "")
        )
        return self.send_response(data=authorization_url)


class SocialCallbackAPIView(NonAuthenticatedAPIMixin, AppAPIView):
    """Common APIView to verify and provide token to login."""

    def get(self, request, *args, **kwargs):
        """Verify user credentials is valid."""

        provider = kwargs["provider"]
        code = request.GET.get("code")
        if not code:
            return self.send_error_response("Authorization code not received.")
        oauth_settings, oauth = get_oauth_details(provider)
        try:
            token = oauth.fetch_access_token(
                oauth_settings.get("token_url"), code=code, client_secret=oauth_settings.get("client_secret")
            )
        except Exception:
            return self.send_error_response("Error fetching access token.")
        user_data = get_user_data(provider, token["access_token"], oauth_settings)
        if not user_data:
            return self.send_error_response("Failed to fetch user data.")
        return self.send_response()