from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_managers

from .models import Post, Reply, User

# register signal
# reply created signal
# profile changed signal

# D6.4
# created - булевая, есть или нет объект в БД
@receiver(post_save, sender=Reply)
def notify_managers_appointment(sender, instance, created, **kwargs):
    if created:
        subject = f'Новый отклик{instance.text}'
    else:
        subject = f'Изменения в статье  {instance.ttext} {instance.d_time.strftime("%d %m %Y")}'
    # recipient_list = []
    #
    # for category in instance.category.all():
    #     for user in category.subscribers.all():
    #         # print(user.email)
    #         # print(user)
    #         recipient_list.append(user.email)
    #
    # print(recipient_list)
    # reply = Reply.objects.get(id=reply_id)
    print(('sender', sender))
    print('instance', instance)

    # send_mail(
    #     subject=f'MMO Portal: новый отклик {instance.title} вышла в {instance.d_time.strftime("%d %m %Y")}',
    #     message=f'новая статья {instance.text} .'
    #             f'Посмотреть принятые отклики:\nhttp://127.0.0.1:8000/responses',
    #     from_email='apractikant@yandex.ru',
    #     recipient_list=recipient_list,
    # )
    print('Опубликована новая статья: ', f'{instance.text} {instance.d_time.strftime("%d %m %Y")}')

