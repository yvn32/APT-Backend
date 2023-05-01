from rest_framework import routers
from django.urls import path, include
from .api import ClientaViewSet, ComunaViewSet, EntradaViewSet, InventarioViewSet, ItemViewSet, PaisViewSet, ParametroViewSet, PerfilViewSet, ProveedoraViewSet, RegionViewSet, RepLegalViewSet, SalidaViewSet, UnidadViewSet, UsuariaViewSet, LoginView, CierreSesionView, CambioPwdView

router = routers.DefaultRouter()

router.register('api/clienta', ClientaViewSet, 'clienta')
router.register('api/comuna', ComunaViewSet, 'comuna')
router.register('api/entrada', EntradaViewSet, 'entrada')
router.register('api/inventario', InventarioViewSet, 'inventario')
router.register('api/item', ItemViewSet, 'item')
router.register('api/pais', PaisViewSet, 'pais')
router.register('api/parametro', ParametroViewSet, 'parametro')
router.register('api/perfil', PerfilViewSet, 'perfil')
router.register('api/proveedora', ProveedoraViewSet, 'proveedora')
router.register('api/region', RegionViewSet, 'region')
router.register('api/replegal', RepLegalViewSet, 'replegal')
router.register('api/salida', SalidaViewSet, 'salida')
router.register('api/unidad', UnidadViewSet, 'unidad')
router.register('api/usuaria', UsuariaViewSet, 'usuaria')

urlpatterns = [
    path('', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/cierreSesion/', CierreSesionView.as_view(), name='cierreSesion'),
    path('api/cambioPwd/', CambioPwdView.as_view(), name='cambioPwd'),
]

# urlpatterns = router.urls
