from django.db.models import Q
from rest_framework import viewsets

from .models import Order, Flavour, Pizza, Customer
from .serializers import OrderSerializer, FlavourSerializer, PizzaSerializer, \
    CustomerSerializer, PizzaCreateSerializer, OrderCreateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')

    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all().prefetch_related('pizzas')
        customer_name = self.request.query_params.get('customer_name')
        status = self.request.query_params.get('status')
        if customer_name or status:
            # possibility filter by order status and customer name via ?customer_name=..&status=...
            queryset = queryset.filter(Q(customer__name=customer_name) | Q(status=status))
        return queryset


class CustomerViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class PizzaViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')

    queryset = Pizza.objects.all().prefetch_related('flavours')
    serializer_class = PizzaSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PizzaCreateSerializer
        return PizzaSerializer


class FlavourViewSet(viewsets.ModelViewSet):
    http_method_names = ('get', 'post', 'patch', 'delete')

    queryset = Flavour.objects.all()
    serializer_class = FlavourSerializer
