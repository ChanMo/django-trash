from django.apps import AppConfig


class TrashConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trash'

    def ready(self):
        import trash.receivers
