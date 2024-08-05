from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import TaskListCreateView, TaskDetailView, UserCreateView, TaskPermissionListCreateView, TaskPermissionDetailView

urlpatterns = [
    # Маршрут для списка задач и создания новых задач
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),

    # Маршрут для получения, обновления и удаления конкретной задачи по id
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # Маршрут для регистрации нового пользователя
    path('register/', UserCreateView.as_view(), name='register'),

    # Маршрут для полуения токена доступа
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),

    # Маршрут для обновления токена доступа
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Маршрут для получения списка разрешений и создания новых разрешений
    path('permissions/', TaskPermissionListCreateView.as_view(), name='task-permission-list-create'),

    # Маршрут для получения, обновления и удаления конкретного разрешения по id
    path('permissions/<int:pk>/', TaskPermissionDetailView.as_view(), name='task-permission-detail')
]