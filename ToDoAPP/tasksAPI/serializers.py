from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, Task, TaskPermission


class UserSerializer(serializers.ModelSerializer):
    # Сериализатор для модели пользователя
    password = serializers.CharField(write_only=True)  # Поле пароля, доступно только для записи

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # Метод создания нового пользователя
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class TaskSerializer(serializers.ModelSerializer):  # Сериализатор для модели задач
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'last_updated_at', 'creator']


class TaskPermissionSerializer(serializers.ModelSerializer):  # Сериализатор для модели разрешений
    class Meta:
        model = TaskPermission
        fields = ['id', 'task', 'user', 'permission']