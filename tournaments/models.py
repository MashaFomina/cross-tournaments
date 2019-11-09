from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
import django
import datetime


class TournamentConfig:
    max_hints_per_task = 3
    duration_hours = 5
    group_name = 'players'


# class TeamUser(AbstractUser):
#     pass
#     # @property
#     # def task_done_cnt(self):
#     #     return self.progresses.filter(status=TaskProgress.DONE).count()

#     # @property
#     # def fine_time(self):
#     #     return sum(p.fine_time() for p in self.progresses.all())


class Tournament(models.Model):
    start_date = models.DateTimeField('start date')

    @property
    def end_date(self):
        return self.start_date + datetime.timedelta(hours=TournamentConfig.duration_hours)

    def is_active(self):
        return self.end_date >= timezone.now()

class Task(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete = models.CASCADE, related_name='tasks')
    title = models.CharField('title', max_length = 100)
    text = models.CharField('text', max_length = 300)
    response = models.CharField('response', max_length = 300)
    x = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    y = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    def __str__(self):
        return self.title + ':' + self.text


class Hint(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE, related_name='hints')
    text = models.CharField('text', max_length = 300)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.task.hints.count() < TournamentConfig.max_hints_per_task:
            super(Hint, self).save()
        else:
            raise Exception(f'{self.task.title} has already {TournamentConfig.max_hints_per_task} hints. No more are allowed!')


class UsedHint(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE, related_name='used_hints')
    owner = models.ForeignKey('auth.User', related_name='owner', on_delete=models.CASCADE) # TeamUser
    hint = models.ForeignKey(Hint, on_delete = models.CASCADE, related_name='hint')


class TaskProgress(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE, related_name='progress')
    owner = models.ForeignKey('auth.User', related_name='progresses', on_delete=models.CASCADE) # TeamUser
    end_date = models.DateTimeField('ent date', null=True, default=None)
    attempts = models.IntegerField('attempt counter', default=0)
    DONE = 2
    PROGRESS = 1
    PLANNED = 0
    STATUS_CHOICES = [
        (DONE, 'done'),
        (PROGRESS, 'progress'),
        (PLANNED, 'planned'),
    ]
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    fine_time = models.FloatField('fine time', default=0, validators=[MinValueValidator(0)]) 
