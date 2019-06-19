from rest_framework import routers

from .views import OrderViewSet, CustomerViewSet, PizzaViewSet, FlavourViewSet

router = routers.DefaultRouter()

router.register('orders', OrderViewSet, basename='orders')
router.register('customers', CustomerViewSet, basename='customers')
router.register('pizzas', PizzaViewSet, basename='pizzas')
router.register('flavours', FlavourViewSet, basename='flavours')
urlpatterns = router.urls
