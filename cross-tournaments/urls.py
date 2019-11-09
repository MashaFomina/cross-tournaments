from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url

from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# from django_mysite.apps.rest import views

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

schema_view = get_swagger_view(title='Cross tournaments API')

urlpatterns = [
    url(r'^api_doc/$', schema_view),
    path('', include(router.urls)),
    url(r'^tournaments/', include('tournaments.urls')),
    path('admin/', admin.site.urls),
    url(r'^api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api/token/verify/$', TokenVerifyView.as_view(), name='token_verify'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
