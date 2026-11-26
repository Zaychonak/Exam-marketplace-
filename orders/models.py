from django.db import models
from users.models import User
from products.models import Product


class Karzina(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="karzina_user")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='karzina_product')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username}: {self.product.title}"


class Zakaz(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_user")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id} ({self.status})"


class SostavZakaza(models.Model):
    zakaz = models.ForeignKey(Zakaz, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Позиция #{self.id} к заказу #{self.zakaz.id}"


class Oplata(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
    )
    METHOD_CHOICES = (
        ('card', 'Банковская карта'),
        ('wallet', 'Электронный кошелек'),
        ('cash', 'Наличные'),
    )

    zakaz = models.OneToOneField(Zakaz, on_delete=models.CASCADE, related_name="oplata_zakaz")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="oplata_user")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='card')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Оплата #{self.id} для заказа #{self.zakaz.id}"


class Vozvrat(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Заявка создана'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    )

    sostav_zakaza = models.ForeignKey(SostavZakaza, on_delete=models.CASCADE, related_name="return_zakaz")
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Возврат #{self.id} ({self.status})"
