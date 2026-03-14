# core/views.py
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
from django.contrib.auth.models import User
from django.shortcuts import render

def index(request):
    return render(request, 'postbox/index.html')


@login_required
def mail_list(request):
    """Получает список писем. Можно передать ?folder=inbox"""
    folder = request.GET.get('folder', 'inbox')
    messages = Message.objects.filter(
        (Q(sender=request.user) | Q(recipient=request.user)) & Q(folder=folder)
    )

    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'subject': msg.subject,
            'sender': msg.sender.username,
            'is_read': msg.is_read,
            'date': str(msg.created_at)
        })

    return JsonResponse({'messages': data})

@login_required
def mail_detail(request, message_id):
    """Просмотр письма + прочитано"""
    try:
        msg = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    # Проверка прав: только свои письма
    if msg.sender != request.user and msg.recipient != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)

    if msg.recipient == request.user and not msg.is_read:
        msg.is_read = True
        msg.save()

    return JsonResponse({
        'id': msg.id,
        'subject': msg.subject,
        'body': msg.body,
        'sender': msg.sender.username,
        'recipient': msg.recipient.username,
        'is_read': msg.is_read,
        'folder': msg.folder
    })

@login_required
def send_mail(request):
    """Отправка письма """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST'}, status=400)

    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        subject = data.get('subject')
        body = data.get('body')

        recipient = User.objects.get(id=recipient_id)

        Message.objects.create(
            sender=request.user, recipient=recipient,
            subject=subject, body=body, folder='inbox'
        )
        Message.objects.create(
            sender=request.user, recipient=recipient,
            subject=subject, body=body, folder='sent', is_read=True
        )

        return JsonResponse({'status': 'sent'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def move_mail(request, message_id):
    """Перемещение письма"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST'}, status=400)

    try:
        msg = Message.objects.get(id=message_id)
        if msg.sender != request.user and msg.recipient != request.user:
            return JsonResponse({'error': 'Access denied'}, status=403)

        data = json.loads(request.body)
        new_folder = data.get('folder')

        valid_folders = ['inbox', 'sent', 'trash', 'archive']
        if new_folder in valid_folders:
            msg.folder = new_folder
            msg.save()
            return JsonResponse({'status': 'moved', 'folder': new_folder})
        else:
            return JsonResponse({'error': 'Invalid folder'}, status=400)

    except Message.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

@login_required
def delete_mail(request, message_id):
    """Удаление"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST'}, status=400)

    try:
        msg = Message.objects.get(id=message_id)
        if msg.sender != request.user and msg.recipient != request.user:
            return JsonResponse({'error': 'Access denied'}, status=403)

        msg.delete()
        return JsonResponse({'status': 'deleted'})
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)