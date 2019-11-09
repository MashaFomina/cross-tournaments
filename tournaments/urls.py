from django.urls import path

from . import views


app_name = 'tournaments'
urlpatterns = [
    path('', views.TournamentList.as_view(), name='list_tournaments'),
    path('tasks/<int:tournament_pk>', views.TaskList.as_view()),
    path('tasks/<int:pk>/', views.submit_task_response, name='submit_task_response'),
    path(r'users/<int:tournament_pk>/', views.UserList.as_view()),
    path('hints/<int:pk>/', views.open_task_hint, name='open_task_hint'),
]
