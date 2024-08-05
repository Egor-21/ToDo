from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # Модель пользователя, которая наследуется от стандартной модели пользователя Django
    def __str__(self):
        return self.username


class Task(models.Model):
    # Модель задачи
    title = models.CharField(max_length=150)  # Название задачи
    description = models.TextField(blank=True)  # Описание задачи, может быть пустым
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания
    last_updated_at = models.DateTimeField(auto_now=True)  # Дата и время последнего изменения

    # Создатель задачи, связь с пользователем
    creator = models.ForeignKey(CustomUser, related_name='tasks', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TaskPermission(models.Model):
    # Модель разрешений для задач
    READ = 'read'
    UPDATE = 'update'

    # Варианты выбора типа разрешения
    PERMISSION_CHOICES = [
        (READ, 'Read'),
        (UPDATE, 'Update')
    ]

    task = models.ForeignKey(Task, related_name='permissions', on_delete=models.CASCADE)  # Связь с задачей
    user = models.ForeignKey(CustomUser, related_name='permissions', on_delete=models.CASCADE) # Связь с пользователем, которому выдали разрешение
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)  # Тип разрешения

    class Meta:
        unique_together = ('task', 'user', 'permission')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Если назначается разрешение на редактирование, то автоматически назначется разрешение на чтение
        if self.permission == TaskPermission.UPDATE:
            TaskPermission.objects.get_or_create(
                task=self.task,
                user=self.user,
                permission=TaskPermission.READ
            )

    def __str__(self):
        return f"Задача: {self.task.title}, Создатель: {self.task.creator.username}, Пользователь: {self.user.username}, Разрешение: {self.permission}"
