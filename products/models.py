from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from users.models import User, Profile



class Market(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_user')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.user.username}'


class Brande(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='product_market')
    brande = models.ForeignKey(Brande, on_delete=models.SET_NULL, related_name='product_brande', null=True, blank=True,)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_category')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    article = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to="products/", blank = True)

    def __str__(self):
        return f'{self.title} - {self.article}'    


class Sklad(models.Model):
    city = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"{self.city}, {self.address}"


class Ostatki_na_sklade(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks_product")
    sklad = models.ForeignKey(Sklad, on_delete=models.CASCADE, related_name="stocks_sklad")
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "sklad")

    def __str__(self):
        return f"{self.product.title} — {self.quantity}"



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews_product")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_user")
    stars = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} — {self.stars}"