# core/models.py
from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    FOLDER_CHOICES = [
        ('inbox', 'Входящие'),
        ('sent', 'Отправленные'),
        ('trash', 'Корзина'),
        ('archive', 'Архив'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    folder = models.CharField(max_length=10, choices=FOLDER_CHOICES, default='inbox')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} ({self.sender.username} -> {self.recipient.username})"

    def to_dict(self):
        """Преобразует объект Message в словарь для сериализации в JSON."""
        return {
            'id': self.id,
            'sender': self.sender.username,
            'recipient': self.recipient.username,
            'subject': self.subject,
            'body': self.body,
            'is_read': self.is_read,
            'folder': self.folder,
            'created_at': self.created_at.isoformat()
        }
