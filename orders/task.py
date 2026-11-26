from celery import shared_task
from django.core.mail import send_mail
from django.db.models import F
from products.models import Ostatki_na_sklade
from .models import Zakaz


@shared_task
def send_order_confirmation_email(zakaz_id):
    """Отправляет чек покупателю в фоне."""
    zakaz = Zakaz.objects.select_related('user').get(id=zakaz_id)
    send_mail(
        subject=f"Заказ #{zakaz.id} успешно оформлен!",
        message=f"Здравствуйте, {zakaz.user.username}! Ваш заказ #{zakaz.id} на сумму {zakaz.total_price} сомони принят.",
        from_email='noreply@marketplace.tj',
        recipient_list=[zakaz.user.email],
        fail_silently=False,
    )
    return f"Email по заказу #{zakaz.id} отправлен"


@shared_task
def cancel_unpaid_order(zakaz_id):
    """Автоматически отменяет неоплаченный заказ через таймер и возвращает товары на склад."""
    zakaz = Zakaz.objects.prefetch_related('items').filter(id=zakaz_id).first()
    if zakaz and zakaz.status == 'pending':
        zakaz.status = 'cancelled'
        zakaz.save()

        for item in zakaz.items.all():
            ostatok = Ostatki_na_sklade.objects.filter(product=item.product).first()
            if ostatok:
                ostatok.quantity = F('quantity') + item.quantity
                ostatok.save()
        return f"Заказ #{zakaz.id} отменен из-за неоплаты, товары возвращены на склад"
    return f"Заказ #{zakaz_id} уже оплачен"
