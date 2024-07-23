from django.core.management import call_command

from apps.common.management.commands.base import AppBaseCommand


class Command(AppBaseCommand):
    help = "Initializes the app by running the necessary initial commands."

    def handle(self, *args, **kwargs):
        """Call all the necessary commands."""

        call_command("migrate")
       