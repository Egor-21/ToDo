from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import CustomUser, Task, TaskPermission


class APITests(APITestCase):
    def setUp(self):
        # Создание тестовых пользоватлей и задачи
        self.user1 = CustomUser.objects.create_user(username='user1', email='user1@gmail.com', password='1234')
        self.user2 = CustomUser.objects.create_user(username='user2', email='user2@gmail.com', password='1234')
        self.task1 = Task.objects.create(title='Task 1', description='Description Task 1', creator=self.user1)

        # Установка URL для тестов
        self.register_url = reverse('register')
        self.token_url = reverse('token-obtain-pair')
        self.task_list_create_url = reverse('task-list-create')
        self.task_detail_url = reverse('task-detail', kwargs={'pk': self.task1.pk})
        self.permissions_list_create_url = reverse('task-permission-list-create')
        self.permissions_detail_url = lambda pk: reverse('task-permission-detail', kwargs={'pk': pk})

    def authenticate(self, username, password):
        # Метод аутентификации и установки токена
        response = self.client.post(self.token_url, {'username': username, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_user_registration(self):
        # Тест регистрации нового пользователя
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@gmail.com',
            'password': '12345'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_task(self):
        # Тест добавления новой задачи
        self.authenticate('user1', '1234')
        response = self.client.post(self.task_list_create_url, {
            'title': 'New Task',
            'description': 'New Task Description'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['creator']['username'], 'user1')

    def test_give_update_permission(self):
        # Тест предоставления прав на редактирование задачи другому пользователю
        self.authenticate('user1', '1234')
        response = self.client.post(self.permissions_list_create_url, {
            'task': self.task1.pk,
            'user': self.user2.pk,
            'permission': 'update'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskPermission.objects.filter(task=self.task1, user=self.user2).count(), 2)  # Update and Read

    def test_update_task_with_permission(self):
        # Тест редактирования задачи пользоватем,который имеет права на редактирование
        TaskPermission.objects.create(task=self.task1, user=self.user2, permission='update')

        # Аутентификация под user2
        self.authenticate('user2', '1234')

        # Редактирование задачи
        response = self.client.patch(self.task_detail_url, {
            'description': 'Updated Description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated Description')

    def test_permission_update(self):
        self.authenticate('user1', '1234')

        # Тест обновления прав доступа на задачу
        permission = TaskPermission.objects.create(task=self.task1, user=self.user2, permission='read')

        # Изменение 'permission' до 'update'
        response = self.client.patch(self.permissions_detail_url(permission.pk), {
            'permission': 'update'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['permission'], 'update')

    def test_permission_denied_for_non_creator(self):
        # Тест на отказ изменять права доступа, если пользователем не является создателем задачи
        self.authenticate('user2', '1234')
        response = self.client.post(self.permissions_list_create_url, {
            'task': self.task1.pk,
            'user': self.user2.pk,
            'permission': 'update'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_workflow(self):  # Тест, покрывающий весь рабочий процесс
        # Регистрация пользователя testuser1
        response = self.client.post(self.register_url, {
            'username': 'testuser1',
            'email': 'testuser1@gmail.com',
            'password': '1234'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Регистрация пользователя testuser2
        response = self.client.post(self.register_url, {
            'username': 'testuser2',
            'email': 'testuser2@gmail.com',
            'password': '12345'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Вход под testuser1
        self.authenticate('testuser1', '1234')

        # Добавление новой задачи от testuser1
        response = self.client.post(self.task_list_create_url, {
            'title': 'Test Task',
            'description': 'Description Test Task'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task_id = response.data['id']

        # Предоставление доступа на редактирование задачи пользователю testuser2
        response = self.client.post(self.permissions_list_create_url, {
            'task': task_id,
            'user': CustomUser.objects.get(username='testuser2').id,
            'permission': 'update'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Выход из учетной записи (сброс токена)
        self.client.credentials()

        # Вход под testuser2
        self.authenticate('testuser2', '12345')

        # Редактирование записи пользователя testuser1 под учетной записью testuser2
        task_detail_url = reverse('task-detail', kwargs={'pk': task_id})
        response = self.client.patch(task_detail_url, {
            'description': 'Updated Description by testuser2'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated Description by testuser2')