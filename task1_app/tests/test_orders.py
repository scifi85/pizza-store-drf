import pytest
from rest_framework.test import APIClient

from api_v1.models import OrderStatus, PizzaSize, Pizza, Order
from tests.factories import PizzaFactory, FlavourFactory, CustomerFactory, OrderFactory


@pytest.fixture
def apiclient():
    return APIClient()


class BaseOrdersAPI:
    @property
    def list_url(self):
        return '/api/orders/'

    @staticmethod
    def detail_url(order_id):
        return f'/api/orders/{order_id}/'

    @staticmethod
    def create_pizza(flavours, **kwargs):
        return PizzaFactory.create(flavours=flavours, **kwargs)

    @staticmethod
    def create_order(pizzas, customer, **kwargs):
        return OrderFactory.create(pizzas=pizzas, customer=customer, **kwargs)


@pytest.mark.django_db
class TestOrdersCRUD(BaseOrdersAPI):
    def test_orders_list_returns_200(self, apiclient):
        response = apiclient.get(self.list_url)
        assert response.status_code == 200

    def test_orders_list_get(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(),))
        customer = CustomerFactory()
        self.create_order((pizza,), customer)
        response = apiclient.get(self.list_url)

        expected_data = [{'id': 1, 'total_sum': 15,
                         'customer': {'id': 1,
                                      'name': 'customer-0',
                                      'phone_number': '+11111111111111',
                                      'address': 'some address'},
                          'pizzas': [
                             {'id': 1,
                              'size': 'l',
                              'price': 15,
                              'flavours': [
                                  {'id': 1, 'name':
                                      'flavour-0',
                                   'added_price': 5}
                              ]
                              }
                         ],
                         'pizza_count': 1,
                         'status': 'init'}]
        assert response.json() == expected_data

    def test_order_post_201(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(),))
        customer = CustomerFactory()
        data = {'pizzas': [pizza.id], 'status': OrderStatus.STATUS_INIT, 'customer': customer.id}
        response = apiclient.post(self.list_url, data=data)
        assert response.status_code == 201

    def test_order_post(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(),))
        customer = CustomerFactory()
        data = {'pizzas': [pizza.id], 'status': OrderStatus.STATUS_INIT, 'customer': customer.id}
        result = apiclient.post(self.list_url, data=data).json()

        assert result['pizzas'] == [pizza.id]
        assert result['status'] == 'init'
        assert result['customer'] == customer.id
        assert result['total_sum'] == 15

    def test_order_patch_200(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(),))
        customer = CustomerFactory()
        order = self.create_order((pizza,), customer)
        pizza2 = self.create_pizza((FlavourFactory(),), size=PizzaSize.SIZE_XXL)
        data = {'pizzas': [pizza2.id]}
        response = apiclient.patch(self.detail_url(order.id), data=data)
        assert response.status_code == 200

    def test_order_patch(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(),))
        customer = CustomerFactory()
        order = self.create_order((pizza,), customer)
        pizza2 = self.create_pizza((FlavourFactory(name='some_flavour'),), size=PizzaSize.SIZE_XXL)
        data = {'pizzas': [pizza2.id]}
        result = apiclient.patch(self.detail_url(order.id), data=data).json()
        assert result['pizzas'][0] == pizza2.id
        pizza_obj = Pizza.objects.get(pk=pizza2.id)
        assert pizza_obj

    def test_order_delete(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(),))
        customer = CustomerFactory()
        order = self.create_order((pizza,), customer)
        result = apiclient.get(self.detail_url(order.id)).json()
        assert result['id'] == order.id
        response = apiclient.delete(self.detail_url(order.id))
        assert response.status_code == 204
        response = apiclient.get(self.detail_url(order.id))
        assert response.status_code == 404
        assert not Order.objects.filter(pk=order.pk).exists()

    def test_order_price_standard(self, apiclient):
        pizza = self.create_pizza((FlavourFactory(added_price=100),))
        # pizza base_price = 10 + flavours added price
        assert pizza.price == 110
        customer = CustomerFactory()
        order = self.create_order((pizza,), customer)
        assert order.total_sum == 110

    def test_order_price_xl(self, apiclient):
        # XL size has price coefficient 1.25
        pizza = self.create_pizza((FlavourFactory(added_price=100),), size=PizzaSize.SIZE_XL)
        customer = CustomerFactory()
        order = self.create_order((pizza,), customer)
        assert order.total_sum == 137

    def test_order_price_xxl(self, apiclient):
        # XXL size has coefficient 1.5
        pizza = self.create_pizza((FlavourFactory(added_price=100),), size=PizzaSize.SIZE_XXL)
        customer = CustomerFactory()
        order = self.create_order((pizza,), customer)
        assert order.total_sum == 165



