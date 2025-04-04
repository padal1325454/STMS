from django.urls import path
from . import views

app_name = 'SmartTaskManagementSystem'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),  
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('create/', views.create_task, name='create_task'),
    path('update/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('notifications/', views.notifications, name='notifications'),
    #path('github/', views.github_issues, name='github'),
    path("github/issues/", views.github_issues, name="github"),
    path('reports/', views.generate_report, name='reports'),
]
