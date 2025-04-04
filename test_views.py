from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from SmartTaskManagementSystem.models import Task, Notification, Report
from SmartTaskManagementSystem.forms import TaskForm, SignupForm, LoginForm, ReportForm
from SmartTaskManagementSystem.views import (
    user_login, user_signup, user_logout, dashboard, create_task,
    update_task_status, github_issues, notifications, generate_report
)
import requests
from unittest.mock import patch, Mock

class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.task = Task.objects.create(title='Test Task', description='Test Description', assignee=self.user)

    def test_user_login_get(self):
        response = self.client.get(reverse('SmartTaskManagementSystem:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SmartTaskManagementSystem/login.html')

    def test_user_login_post_valid(self):
        response = self.client.post(reverse('SmartTaskManagementSystem:login'), {'email': 'test@example.com', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('SmartTaskManagementSystem:dashboard'))

    def test_user_login_post_invalid(self):
        response = self.client.post(reverse('SmartTaskManagementSystem:login'), {'email': 'test@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password.', response.content)

    def test_user_signup_get(self):
        response = self.client.get(reverse('SmartTaskManagementSystem:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SmartTaskManagementSystem/signup.html')

    def test_user_signup_post_valid(self):
        response = self.client.post(reverse('SmartTaskManagementSystem:signup'), {'email': 'newuser@example.com', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('SmartTaskManagementSystem:dashboard'))

    def test_user_logout(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('SmartTaskManagementSystem:login'))

    def test_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks.html')

    def test_create_task_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:create_task'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SmartTaskManagementSystem/create_task.html')

    def test_create_task_post_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('SmartTaskManagementSystem:create_task'), {'title': 'New Task', 'description': 'New Description', 'status': 'TODO'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('SmartTaskManagementSystem:dashboard'))

    def test_update_task_status_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:update_task_status', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SmartTaskManagementSystem/update_task.html')

    def test_update_task_status_post_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('SmartTaskManagementSystem:update_task_status', args=[self.task.id]), {'status': 'DONE'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('SmartTaskManagementSystem:dashboard'))
        updated_task = Task.objects.get(id=self.task.id)
        self.assertEqual(updated_task.status, 'DONE')
        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 1)

    @patch('requests.get')
    def test_github_issues(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'title': 'Issue 1'}]
        mock_get.return_value = mock_response
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:github_issues'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SmartTaskManagementSystem/github.html')
        self.assertEqual(len(response.context['issues']), 1)

    def test_notifications(self):
        Notification.objects.create(message='Test Notification', recipient=self.user)
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'SmartTaskManagementSystem/notifications.html')
        self.assertEqual(len(response.context['notifications']), 1)

    def test_generate_report_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('SmartTaskManagementSystem:reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "SmartTaskManagementSystem/reports.html")

    def test_generate_report_post_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('SmartTaskManagementSystem:reports'),{'title':'Report 1','content':'Report Content'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('SmartTaskManagementSystem:reports'))
        self.assertEqual(Report.objects.filter(generated_by=self.user).count(), 1)