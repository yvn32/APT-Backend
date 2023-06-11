from rest_framework import routers
from django.urls import path, include
from .api import ClientaViewSet, ComunaViewSet, DetalleIngredienteViewSet, DetallePedidoViewSet, DetallePreparacionViewSet, EntradaViewSet, EstadoPedidoViewSet, FtViewSet, InventarioViewSet, ItemViewSet, PaisViewSet, ParametroViewSet, PedidoViewSet, PerfilViewSet, ProveedoraViewSet, RegionViewSet, RepLegalViewSet, SalidaViewSet, UnidadViewSet, UsuariaViewSet
from .api import LoginView, CierreSesionView, CambioPwdView, SimularFTAPIView, ValidarStockPedidoAPIView, AsignarUsuariaAPIView, ActualizarEstadoPedidoAPIView
from django.conf import settings
from django.conf.urls.static import static


router = routers.DefaultRouter()

router.register('api/clienta', ClientaViewSet, 'clienta')
router.register('api/comuna', ComunaViewSet, 'comuna')
router.register('api/detalleingrediente', DetalleIngredienteViewSet, 'detalleingrediente')
router.register('api/detallepedido', DetallePedidoViewSet, 'detallepedido')
router.register('api/detallepreparacion', DetallePreparacionViewSet, 'detallepreparacion')
router.register('api/entrada', EntradaViewSet, 'entrada')
router.register('api/estadopedido', EstadoPedidoViewSet, 'estadopedido')
router.register('api/ft', FtViewSet, 'ft')
router.register('api/inventario', InventarioViewSet, 'inventario')
router.register('api/item', ItemViewSet, 'item')
router.register('api/pais', PaisViewSet, 'pais')
router.register('api/parametro', ParametroViewSet, 'parametro')
router.register('api/pedido', PedidoViewSet, 'pedido')
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

    path('api/simularFt/', SimularFTAPIView.as_view(), name='simularFt'),
    
    path('api/validarStockPedido/<int:cod_pedido>/', ValidarStockPedidoAPIView.as_view(), name='validarStockPedido'), #PARA PRUEBAS
    path('api/asignarUsuaria/', AsignarUsuariaAPIView.as_view(), name='asignarUsuaria'),
    path('api/actualizarEstadoPedido/', ActualizarEstadoPedidoAPIView.as_view(), name='actualizarEstadoPedido'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = router.urls
