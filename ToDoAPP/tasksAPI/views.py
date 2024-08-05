from django.shortcuts import get_object_or_404
from django.db.models import Q
from .serializers import TaskSerializer, UserSerializer, TaskPermissionSerializer
from rest_framework import generics, permissions
from .models import Task, TaskPermission
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied


class UserCreateView(generics.CreateAPIView):
    # Представление для создания нового пользователя
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TaskListCreateView(generics.ListCreateAPIView):
    # Представление для получения списка задач и создание новых задач
    # Только авторизованные пользователи могут видеть и создавать задачи
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Метод для создания мадачи, с указанием создателя
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        # Метод для отображения задач, доступных пользователю
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(Q(creator=user) |
                                       Q(permissions__user=user, permissions__permission=TaskPermission.READ)).distinct()
        return Task.objects.none()  # Если пользователь не авторизован, возвращаем пустой список


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Представление для просмотра, обновления и удаления задачи
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        # Метод для получения задачи, с проверкой прав доступа
        task = get_object_or_404(Task, pk=self.kwargs['pk'])
        if task.creator == self.request.user:
            return task
        permission = TaskPermission.objects.filter(task=task, user=self.request.user, permission=TaskPermission.UPDATE).first()
        if not permission:
            raise PermissionDenied("У вас нет доступа для редактирования этой задачи")
        return task


class TaskPermissionListCreateView(generics.ListCreateAPIView):
    # Представление для получения списка разрешений и создания новых разрешений
    queryset = TaskPermission.objects.all()
    serializer_class = TaskPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Метод, для получения разрешений, созданных пользователем
        return TaskPermission.objects.filter(task__creator=self.request.user)

    def perform_create(self, serializer):
        # Метод для создания новых разрешений, с проверкой прав доступа
        task = serializer.validated_data['task']
        if task.creator != self.request.user:
            raise PermissionDenied("Только владелец задачи может назначать разрешения")
        serializer.save()


class TaskPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Представление для получения, обновления и удаления разрешений
    queryset = TaskPermission.objects.all()
    serializer_class = TaskPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskPermission.objects.filter(task__creator=self.request.user)

