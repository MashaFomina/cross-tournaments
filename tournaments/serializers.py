from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Tournament, Task, UsedHint, Hint, TaskProgress


class HintSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hint
        fields = ['id', 'text', 'is_used']


class UsedHintSerializer(serializers.HyperlinkedModelSerializer):
    is_used = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Hint
        fields = ['id', 'text', 'is_used']

    def get_is_used(self, obj):
        return obj.is_used if hasattr(obj, 'is_used') else False


class TaskSimpleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title']


class TaskProgressSerializer(serializers.ModelSerializer):
    # task = serializers.PrimaryKeyRelatedField(read_only = True)
    # task = TaskSimpleSerializer(read_only = True)
    task_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskProgress
        fields = ['end_date', 'attempts', 'status', 'task_id', 'fine_time'] # , 'task', 'owner'

    def get_task_id(self, obj):
        return obj.task.pk


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    # progress = TaskProgressSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    hints = serializers.SerializerMethodField(read_only=True)
    used_hints_cnt = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'text', 'x', 'y', 'hints', 'used_hints_cnt', 'progress']

    def get_hints(self, obj):
        hints = obj.hints.all()
        used_hints_ids = obj.used_hints.all().values_list('hint__pk', flat=True)
        for hint in hints:
            hint.is_used = True if hint.pk in used_hints_ids else False
        return UsedHintSerializer(hints, many=True).data

    def get_progress(self, obj):
        progresses = obj.progress.all()
        if len(progresses) > 0:
            progress = progresses[0]
        else:
            progress = TaskProgress(task=obj, status=TaskProgress.PLANNED)
        return TaskProgressSerializer(progress, many=False).data

    def get_used_hints_cnt(self, obj):
        return obj.used_hints.count()


class UserSerializer(serializers.ModelSerializer):
    progresses = TaskProgressSerializer(many=True)
    # fine_time = serializers.SerializerMethodField()
    # task_done_cnt = serializers.SerializerMethodField()
    fine_time = serializers.FloatField()
    task_done_cnt = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'username', 'task_done_cnt', 'fine_time', 'progresses']

    # def get_task_done_cnt(self, obj):
    #     return obj.progresses.filter(status=TaskProgress.DONE).count()

    # def get_fine_time(self, obj):
    #     return sum(p.fine_time() for p in obj.progresses.all())


class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'start_date', 'end_date']
