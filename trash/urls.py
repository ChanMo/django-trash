from django.urls import path
from . import views
from . import admin


urlpatterns = [
    path('<int:pk>/recovery/', admin.CancelAdminDeleteView.as_view(), name='recovery'),
    path('<int:pk>/permanent_delete/', admin.ForceAdminDeleteView.as_view(), name='permanent_delete'),
    path('<int:pk>/cancel/', views.CancelDeleteView.as_view(), name='cancel'),
    path('<int:pk>/delete/', views.ForceDeleteView.as_view(), name='delete'),
    path('', views.TrashView.as_view(), name='trash_index'),    
]

app_name = 'trash'
