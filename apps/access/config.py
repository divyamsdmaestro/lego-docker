from djchoices import DjangoChoices, ChoiceItem


class UserLoginTypeChoices(DjangoChoices):
    """Choices for User Login Type."""

    website = ChoiceItem("website", "Website")
    google = ChoiceItem("google", "Google")
    facebook = ChoiceItem("facebook", "Facebook")