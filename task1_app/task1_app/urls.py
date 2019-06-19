from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view


schema_view = get_swagger_view(title='Pizza Store API')


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api/', include('api_v1.urls'), name='api'),
    path(r'', schema_view),
]
