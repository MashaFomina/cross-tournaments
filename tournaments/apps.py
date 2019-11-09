from django.apps import AppConfig
from django.db.models.signals import post_migrate


class TournamentsConfig(AppConfig):
    name = 'tournaments'

    def ready(self):
        from .signals import populate_models
        # signal is emitted after every migrate call
        post_migrate.connect(populate_models, sender=self)
