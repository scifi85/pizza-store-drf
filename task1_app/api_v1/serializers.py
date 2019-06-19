from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Order, Customer, Pizza, Flavour, OrderStatus


class OrderSerializer(serializers.ModelSerializer):
    pizza_count = serializers.SerializerMethodField()

    class Meta:
        depth = 2
        model = Order
        fields = ('id', 'total_sum', 'customer', 'pizzas', 'pizza_count', 'status')
        read_only_fields = ('total_sum',)

    @staticmethod
    def get_pizza_count(obj):
        return obj.pizzas.count()


class OrderCreateSerializer(serializers.ModelSerializer):
    # Custom create serializer, DRF dashboard can't show M2M list of objects
    pizza_qs = Pizza.objects.all().prefetch_related('flavours')
    pizzas = serializers.PrimaryKeyRelatedField(queryset=pizza_qs, many=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('total_sum',)

    def create(self, validated_data):
        pizza_data = validated_data.pop('pizzas')
        order = Order.objects.create(**validated_data)
        for pizza in pizza_data:
            pizza, _ = Pizza.objects.get_or_create(id=pizza.id)
            order.pizzas.add(pizza)
        return order

    def update(self, instance, validated_data):
        immutable_statuses = [OrderStatus.STATUS_SHIP, OrderStatus.STATUS_DELIVERED]
        if instance.status in immutable_statuses:
            raise ValidationError(f'Order with statuses {immutable_statuses} can not be changed')
        return super(OrderCreateSerializer, self).update(instance, validated_data)


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'


class PizzaSerializer(serializers.ModelSerializer):
    # main serializer to show all nested related data

    class Meta:
        depth = 1
        model = Pizza
        fields = '__all__'
        read_only_fields = ('price',)


class PizzaCreateSerializer(serializers.ModelSerializer):
    # Custom create serializer, DRF dashboard can't show M2M list of objects
    flavours = serializers.PrimaryKeyRelatedField(queryset=Flavour.objects.all(), many=True)

    class Meta:
        model = Pizza
        fields = '__all__'
        read_only_fields = ('price',)

    def create(self, validated_data):
        flavours_data = validated_data.pop('flavours')
        pizza = Pizza.objects.create(**validated_data)
        for flavour in flavours_data:
            flavour, _ = Flavour.objects.get_or_create(name=flavour.name, added_price=flavour.added_price)
            pizza.flavours.add(flavour)
        return pizza


class FlavourSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flavour
        fields = '__all__'
