from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views
from .views import NotificationPreferencesView

urlpatterns = [
    path("created/", get_user, name="getUser"),
    path("create/", create_user, name="createUser"),
    path("create/<int:pk>", update_user, name="updatesUser"),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('notification-preferences/', NotificationPreferencesView.as_view(), name='notification-preferences')
]
