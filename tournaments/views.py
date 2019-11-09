import datetime
from functools import reduce

from django.shortcuts import render
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.shortcuts import get_list_or_404
from django.db.models import Count, Sum, Prefetch, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import connection, reset_queries
from django.forms.models import model_to_dict

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics, filters
from rest_framework import permissions
from rest_framework import renderers

from .models import Task, TaskProgress, TournamentConfig, Hint, UsedHint, Tournament
from .serializers import TaskSerializer, UserSerializer, TournamentSerializer


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)): # | u.is_superuser:
                return True

        # In case the 403 handler should be called raise the exception
        raise PermissionDenied

    return user_passes_test(in_groups, login_url='403')


def calculate_fine_time(task, progress):
    used_hints = task.used_hints.filter(owner=progress.owner)
    fine = datetime.timedelta(minutes=15) * progress.attempts + len(used_hints) * datetime.timedelta(minutes=30)
    fine += (progress.end_date - task.tournament.start_date)
    return fine.total_seconds() / 60


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@group_required(TournamentConfig.group_name)
def submit_task_response(request, pk, format=None):
    """
    Submit task response.
    """
    result = {'success': False}
    try:
        task = Task.objects.get(pk=pk)
        progress = TaskProgress.objects.filter(task=task, owner=request.user)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if now() > task.tournament.end_date:
        result['msg'] = 'Sorry, tournament has already finished!'
    elif 'response' in request.data:
        response = request.data['response']

        if len(progress) > 0:
            progress = progress[0]
        else:
            progress = TaskProgress(task=task, owner=request.user) 

        if progress.status != TaskProgress.DONE:
            progress.attempts += 1
            if task.response == response:
                progress.end_date = now()
                progress.status = TaskProgress.DONE
                progress.fine_time = calculate_fine_time(task, progress)
                result['success'] = True
            else:
                result['msg'] = 'Sorry, your answer is wrong!'
            progress.save()
        else:
            result['msg'] = 'Sorry, you has already answered on this task!'
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@group_required(TournamentConfig.group_name)
def open_task_hint(request, pk, format=None):
    """
    Open hint for task.
    """
    result = {'success': False}
    try:
        hint = Hint.objects.get(pk=pk)
        if now() > hint.task.tournament.end_date:
            result['msg'] = 'Sorry, tournament has already finished!'
        else:
            params = {
                'owner': request.user,
                'hint': hint,
                'task': hint.task
            }
            used_hint = UsedHint.objects.get_or_create(**params)
            result['hint'] = reduce(lambda x,y: dict(x, **y), (model_to_dict(hint) , { 'is_used' : True}))
            result['success'] = True

    except Hint.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(result, status=status.HTTP_200_OK)

class DistinctSum(Sum):
    """
    Sum distinct values.
    """
    function = "SUM"
    template = "%(function)s(DISTINCT %(expressions)s)"

class UserList(generics.ListAPIView):
    """
    This endpoint returns list of users (players) with progress.
    """
    queryset = User.objects.filter(groups__name__in=[TournamentConfig.group_name])
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        tournament_pk = kwargs.get('tournament_pk')
        queryset = self.get_queryset().annotate(
            task_done_cnt=Count(
                'progresses__pk',
                distinct=True,
                filter=Q(progresses__task__tournament__pk=tournament_pk, progresses__status=TaskProgress.DONE),
            ),
            fine_time=Coalesce(Sum(
                'progresses__fine_time',
                filter=Q(progresses__task__tournament__pk=tournament_pk),
            ), 0)
        ).order_by('-task_done_cnt', '-fine_time').prefetch_related(
            Prefetch('progresses', queryset=TaskProgress.objects.filter(task__tournament__pk=tournament_pk))
        )

        result = get_list_or_404(queryset)
        print('connection.queries: ', connection.queries)

        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskList(generics.ListAPIView):
    """
    Return list of tasks filtered by tournament for the current authenticated user.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Filter used hints and progress
        for the current authenticated user.
        """
        user = self.request.user
        return Task.objects.all().prefetch_related(
            Prefetch('progress', queryset=TaskProgress.objects.filter(owner=user))
        ).prefetch_related(
            Prefetch('used_hints', queryset=UsedHint.objects.filter(owner=user))
        )

    def list(self, request, *args, **kwargs):
        """
        Return list of tasks filtered by tournament for the current authenticated user.
        """
        queryset = self.get_queryset()
        tournament_pk = kwargs.get('tournament_pk')
        result = get_list_or_404(
            queryset, tournament__pk=tournament_pk
        )
        serializer = self.get_serializer(result, many=True)
        print('connection.queries: ', connection.queries)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TournamentList(generics.ListAPIView):
    """
    This endpoint returns list of tournaments.
    """
    queryset = Tournament.objects.all().order_by('-start_date')
    serializer_class = TournamentSerializer
