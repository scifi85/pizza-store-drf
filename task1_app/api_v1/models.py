from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver


class Flavour(models.Model):
    name = models.CharField(max_length=300, unique=True)
    added_price = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class PizzaSize:
    SIZE_L = 'l'
    SIZE_XL = 'xl'
    SIZE_XXL = 'xxl'

    SIZE_CHOICES = (
        (SIZE_L, 'L'),
        (SIZE_XL, 'XL'),
        (SIZE_XXL, 'XXL'),
    )


SIZE_PRICE_COEFF_MAP = {
    PizzaSize.SIZE_L: 1,
    PizzaSize.SIZE_XL: 1.25,
    PizzaSize.SIZE_XXL: 1.5
}


class Pizza(models.Model):
    size = models.CharField(max_length=20, choices=PizzaSize.SIZE_CHOICES, default=PizzaSize.SIZE_L)
    flavours = models.ManyToManyField(Flavour)
    # use PositiveInteger for simplicity
    price = models.PositiveIntegerField(default=0)

    def get_price(self):
        base_price = 10
        flavours_price = sum(self.flavours.values_list('added_price', flat=True))
        return (flavours_price + base_price) * SIZE_PRICE_COEFF_MAP[self.size]

    def __str__(self):
        flavours = ', '.join(self.flavours.values_list('name', flat=True))
        return f'{self.size} pizza with {flavours}'


@receiver(m2m_changed, sender=Pizza.flavours.through)
def save_pizza_price(sender, instance, **kwargs):
    # calculate pizza's price after instance was created and m2m related instances were attached to it
    instance.price = instance.get_price()
    instance.save()


@receiver(post_save, sender=Flavour)
def update_pizza_price(sender, instance, **kwargs):
    # recalculate pizza's price if related flavour's price was changed
    for pizza in instance.pizza_set.all():
        pizza.price = pizza.get_price()
        pizza.save()


class Customer(models.Model):
    name = models.CharField(max_length=300)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Format is +111111111111111. Max 15 digits is allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField()

    def __str__(self):
        return self.name


class OrderStatus:
    STATUS_INIT = 'init'
    STATUS_PAID = 'paid'
    STATUS_SHIP = 'shipped'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES = (
        (STATUS_INIT, 'Initial'),
        (STATUS_PAID, 'Paid'),
        (STATUS_SHIP, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
    )


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=OrderStatus.STATUS_CHOICES, default=OrderStatus.STATUS_INIT)
    pizzas = models.ManyToManyField(Pizza)
    # use PositiveInteger for simplicity
    total_sum = models.PositiveIntegerField(default=0)

    def get_total_sum(self):
        return sum(self.pizzas.values_list('price', flat=True))

    def __str__(self):
        return f'Order #{self.id}, sum: {self.total_sum}'


@receiver(m2m_changed, sender=Order.pizzas.through)
def save_order_total_price(sender, instance, **kwargs):
    # calculate order's tota; price after m2m related pizzas were attached to it
    instance.total_sum = instance.get_total_sum()
    instance.save()


@receiver(post_save, sender=Pizza)
def update_order_total_price(sender, instance, **kwargs):
    # recalculate order's total price if related pizza's price was changed
    for order in instance.order_set.all():
        if order.status == OrderStatus.STATUS_INIT:
            # we don't want to change the total sum for already paid, shipped and delivered orders
            order.total_sum = order.get_total_sum()
            order.save()
