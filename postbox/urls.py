from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mail/', views.mail_list, name='mail_list'),
    path('mail/send/', views.send_mail, name='send_mail'),
    path('mail/<int:message_id>/', views.mail_detail, name='mail_detail'),
    path('mail/<int:message_id>/move/', views.move_mail, name='move_mail'),
    path('mail/<int:message_id>/delete/', views.delete_mail, name='delete_mail'),
]