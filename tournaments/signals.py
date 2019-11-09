def populate_models(sender, **kwargs):
    from django.apps import apps
    from .apps import TournamentsConfig
    from django.contrib.auth.models import User, Group, Permission
    from .models import TournamentConfig, Task, Tournament
    from django.contrib.contenttypes.models import ContentType

    # add player group
    if Group.objects.filter(name=TournamentConfig.group_name).count() == 0:
        player_group, created = Group.objects.get_or_create(name=TournamentConfig.group_name)
        models = ['task', 'tournament'] # apps.all_models[TournamentsConfig.name]
        for model in models:
            content_type, _ = ContentType.objects.get_or_create(
                app_label=TournamentsConfig.name,
                model=model.lower()
            )
            permissions = Permission.objects.filter(content_type=content_type, codename__startswith='view_')
            player_group.permissions.add(*permissions)
        player_group.save()
