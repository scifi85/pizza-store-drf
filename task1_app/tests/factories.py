import factory

from api_v1.models import Customer, Order, Pizza, Flavour, PizzaSize, OrderStatus


class CustomerFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "customer-{}".format(n))
    phone_number = '+11111111111111'
    address = 'some address'

    class Meta:
        model = Customer


class FlavourFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "flavour-{}".format(n))
    added_price = 5

    class Meta:
        model = Flavour


class PizzaFactory(factory.django.DjangoModelFactory):
    size = PizzaSize.SIZE_L

    class Meta:
        model = Pizza

    @factory.post_generation
    def flavours(self, create, extracted, **kwargs):
        # for M2M relations via PizzaFactory.create(flavours=(..)). No flavours by default
        if not create:
            return

        if extracted:
            for flavour in extracted:
                self.flavours.add(flavour)


class OrderFactory(factory.django.DjangoModelFactory):
    customer = factory.SubFactory(CustomerFactory)
    status = OrderStatus.STATUS_INIT

    class Meta:
        model = Order

    @factory.post_generation
    def pizzas(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for pizza in extracted:
                self.pizzas.add(pizza)
