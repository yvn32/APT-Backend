from .models import Clienta, Comuna, DetalleIngrediente, DetallePedido, DetallePreparacion, Entrada, EstadoPedido, Ft, Inventario, Item, Pais, Parametro, Pedido, Perfil, Proveedora, Region, RepLegal, Salida,Unidad, Usuaria
from rest_framework import viewsets, permissions, status
from .serializers import ClientaSerializer, ComunaSerializer, DetalleIngredienteSerializer, DetallePedidoSerializer, DetallePreparacionSerializer, EntradaSerializer, EstadoPedidoSerializer, FtSerializer, InventarioSerializer, ItemSerializer, PaisSerializer, ParametroSerializer, PedidoCreateSerializer, PedidoUpdateSerializer, PerfilSerializer, ProveedoraSerializer, RegionSerializer, RepLegalSerializer, SalidaSerializer, UnidadSerializer, UsuariaSerializer
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from functools import partial
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
import os, math
from django.conf import settings
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from datetime import date


class ClientaViewSet(viewsets.ModelViewSet):
    queryset = Clienta.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientaSerializer

class ComunaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comuna.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ComunaSerializer

class DetalleIngredienteViewSet(viewsets.ModelViewSet):
    queryset = DetalleIngrediente.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = DetalleIngredienteSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data

        # Obtener la ficha técnica asociada al detalle de ingrediente
        ft_cod_ft = data.get('ft_cod_ft')
        ft = Ft.objects.get(cod_ft=ft_cod_ft)

        # Obtener el costo del detalle de ingrediente
        cantidad = data.get('cantidad')
        item_cod_item = data.get('item_cod_item')
        item = Item.objects.get(cod_item=item_cod_item)
        costo_det = math.floor(item.costo_std * cantidad / item.cant_item)

        # Crear el detalle de ingrediente
        detalle_ingrediente = DetalleIngrediente.objects.create(
            cantidad=cantidad,
            item_cod_item=item,
            ft_cod_ft=ft,
            costo_det=costo_det
        )

        # Actualizar el costo total de la ficha técnica
        ft.costo_tot += costo_det
        ft.save()

        serializer = self.get_serializer(detalle_ingrediente)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Obtener la ficha técnica asociada al detalle de ingrediente
        ft = instance.ft_cod_ft

        # Actualizar el costo total de la ficha técnica
        ft.costo_tot -= instance.costo_det
        ft.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = DetallePedidoSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        
        # Obtener datos del serializer
        categoria = data.get('categoria')
        ft_cod_ft = data.get('ft_cod_ft')
        item_cod_item = data.get('item_cod_item')
        pedido_cod_pedido = data.get('pedido_cod_pedido')
        cantidad = data.get('cantidad')
        
        # Obtener pedido asociado al detalle de pedido
        pedido = Pedido.objects.get(cod_pedido=pedido_cod_pedido)

        # categoria: 1 = ITEM; 2 = FT
        if categoria == 1:
            if ft_cod_ft is not None or item_cod_item is None:
                return Response({'error': 'Datos inválidos (categoría ítem)'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calcular costo de la línea de detalle
            item = Item.objects.get(cod_item=item_cod_item)
            costo_det = math.floor(item.costo_std * cantidad / item.cant_item)

            # Crear el detalle de pedido
            detalle_pedido = DetallePedido.objects.create(
                pedido_cod_pedido = pedido,
                categoria = categoria,
                item_cod_item = item,
                ft_cod_ft = ft_cod_ft,
                cantidad = cantidad,
                costo_det = costo_det
            ) 
        elif categoria == 2:
            if item_cod_item is not None or ft_cod_ft is None:
                return Response({'error': 'Datos inválidos (categoría ficha técnica)'}, status=status.HTTP_400_BAD_REQUEST)

            # Calcular costo de la línea de detalle
            ft = Ft.objects.get(cod_ft=ft_cod_ft)
            costo_det = math.floor(ft.costo_tot * cantidad / ft.rendimiento)

            # Crear el detalle de pedido
            detalle_pedido = DetallePedido.objects.create(
                pedido_cod_pedido = pedido,
                categoria = categoria,
                item_cod_item = item_cod_item,
                ft_cod_ft = ft,
                cantidad = cantidad,
                costo_det = costo_det
            ) 
        else:
            return Response({'error': 'Categoría invalida'}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar costo total y precio del pedido
        pedido.costo_tot += costo_det
        pedido.precio = math.floor(pedido.costo_tot * (1 + pedido.margen / 100))
        pedido.save()

        serializer = self.get_serializer(detalle_pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DetallePreparacionViewSet(viewsets.ModelViewSet):
    queryset = DetallePreparacion.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = DetallePreparacionSerializer

class EntradaViewSet(viewsets.ModelViewSet):
    queryset = Entrada.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EntradaSerializer

    def create(self, request, *args, **kwargs):       
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        self.perform_create(serializer)

        codigo_articulo = request.data['inventario_cod_art']
        cantidad = request.data['cantidad']
        actualizarInventario(codigo_articulo, cantidad, 1)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class EstadoPedidoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EstadoPedido.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EstadoPedidoSerializer

class FtViewSet(viewsets.ModelViewSet):
    queryset = Ft.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = FtSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        imagen = request.FILES.get('img_ft')

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if imagen:
            self.handle_uploaded_file(imagen, instance)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def handle_uploaded_file(self, file, instance):
        filename = file.name
        filepath = os.path.join('fts', filename)
        destination = open(os.path.join(settings.MEDIA_ROOT, filepath), 'wb+')
        
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        
        instance.img_ft = filepath
        instance.save()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            with transaction.atomic():
                # Eliminar registros asociados en detalle_preparacion y detalle_ingrediente
                DetallePreparacion.objects.filter(ft_cod_ft=instance).delete()
                DetalleIngrediente.objects.filter(ft_cod_ft=instance).delete()

                # Eliminar imagen de la ft
                if instance.img_ft:
                    ruta_img = os.path.join(settings.MEDIA_ROOT, instance.img_ft.name)
                    if os.path.exists(ruta_img):
                        os.remove(ruta_img)

                # Eliminar registro en ft
                self.perform_destroy(instance)

                return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = InventarioSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ItemSerializer

class PaisViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pais.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PaisSerializer

class ParametroViewSet(viewsets.ModelViewSet):
    queryset = Parametro.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ParametroSerializer
    allowed_methods = ['GET', 'PUT', 'PATCH']

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoUpdateSerializer

    def perform_create(self, serializer):
        margen_param = Parametro.objects.get(parametro='MARGEN_VTA')
        serializer.save(margen=margen_param.valor_param)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            with transaction.atomic():
                DetallePedido.objects.filter(pedido_cod_pedido=instance).delete() # Eliminar registros asociados en detalle_pedido
                self.perform_destroy(instance) # Eliminar registro en pedido
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PerfilSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cod_perfil in [1, 2, 3, 4]:
            return Response({'message': 'No está permitido eliminar este perfil'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({'message': 'Perfil eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.cod_perfil in [1, 2, 3, 4]:
            return Response({'message': 'No está permitido actualizar este perfil'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class ProveedoraViewSet(viewsets.ModelViewSet):
    queryset = Proveedora.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProveedoraSerializer

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegionSerializer

class RepLegalViewSet(viewsets.ModelViewSet):
    queryset = RepLegal.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RepLegalSerializer

class SalidaViewSet(viewsets.ModelViewSet):
    queryset = Salida.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SalidaSerializer

    def create(self, request, *args, **kwargs):
        codigo_articulo = request.data['inventario_cod_art']
        cantidad = request.data['cantidad']
        resultado = actualizarInventario(codigo_articulo, cantidad, 2)
        if resultado:
            serializer = self.get_serializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'error': 'No hay stock suficiente'}, status=status.HTTP_400_BAD_REQUEST)

class UnidadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unidad.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UnidadSerializer

class UsuariaViewSet(viewsets.ModelViewSet):
    queryset = Usuaria.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UsuariaSerializer

#==============================   
# MÓDULO 1: USUARIAS
#============================== 

# INICIAR SESIÓN
# canal: 1 = web ; 2 = móvil
# logueada: 0 = no logueada; 1 = logueada web; 2 = logueada móvil; 3 = logueada web y móvil
class LoginView(APIView):
    def post(self, request, format=None):
        correo = ''
        pwd = ''
        canal = 0
        try:
            correo = request.data.get('correo')
            pwd = request.data.get('pwd')
            canal = request.data.get('canal')
            if(canal == 1 or canal == 2):
                resultado = validarPwd(correo, pwd)
                print(validarPwd)
                if resultado:
                    usuaria = Usuaria.objects.get(correo=correo)
                    
                    if((usuaria.logueada == 1 and canal == 1) or (usuaria.logueada == 2 and canal == 2) or usuaria.logueada == 3):
                        return Response({'message': 'La usuaria ya se encuentra logueada'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if(usuaria.logueada == 0 and canal == 1):
                        Usuaria.objects.filter(correo=correo).update(logueada=1)
                        return Response({'message': 'Inicio de sesión web ok'}, status=status.HTTP_200_OK)
                    
                    elif(usuaria.logueada == 0 and canal == 2):
                        Usuaria.objects.filter(correo=correo).update(logueada=2)
                        return Response({'message': 'Inicio de sesión móvil ok'}, status=status.HTTP_200_OK)

                    elif((usuaria.logueada == 1 and canal == 2) or (usuaria.logueada == 2 and canal == 1)):
                        Usuaria.objects.filter(correo=correo).update(logueada=3)
                        return Response({'message': 'Inicio de sesión ok'}, status=status.HTTP_200_OK)

                    else:
                        return Response({'message': 'No es posible iniciar sesión'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Canal de origen no ok'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)

# CERRAR SESIÓN
# canal: 1 = web ; 2 = móvil
# logueada: 0 = no logueada; 1 = logueada web; 2 = logueada móvil; 3 = logueada web y móvil
class CierreSesionView(APIView):
    def post(self, request, format=None):
        correo = ''
        canal = 0
        try:
            correo = request.data.get('correo')
            canal = request.data.get('canal')
            if(canal == 1 or canal == 2):
                usuaria = Usuaria.objects.get(correo=correo)
                
                if(usuaria.logueada == 0 or (usuaria.logueada == 1 and canal == 2) or (usuaria.logueada == 2 and canal == 1)):
                    return Response({'message': 'No es posible cerrar sesión porque la usuaria no está logueada'}, status=status.HTTP_400_BAD_REQUEST)
                
                if(usuaria.logueada == 1 and canal == 1):
                    Usuaria.objects.filter(correo=correo).update(logueada=0)
                    return Response({'message': 'Cierre de sesión web ok'}, status=status.HTTP_200_OK)
                
                elif(usuaria.logueada == 2 and canal == 2):
                    Usuaria.objects.filter(correo=correo).update(logueada=0)
                    return Response({'message': 'Cierre de sesión móvil ok'}, status=status.HTTP_200_OK)

                elif(usuaria.logueada == 3 and canal == 1):
                    Usuaria.objects.filter(correo=correo).update(logueada=2)
                    return Response({'message': 'Cierre de sesión web ok'}, status=status.HTTP_200_OK)

                elif(usuaria.logueada == 3 and canal == 2):
                    Usuaria.objects.filter(correo=correo).update(logueada=1)
                    return Response({'message': 'Cierre de sesión móvil ok'}, status=status.HTTP_200_OK)

                else:
                    return Response({'message': 'No es posible cerrar la sesión'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Canal de origen no ok'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Datos inválidos'}, status=status.HTTP_400_BAD_REQUEST)

# CAMBIAR CONTRASEÑA
class CambioPwdView(APIView):
    def patch(self, request, format=None):
        correo = ''
        newPwd = ''
        pwd = ''
        try:
            correo = request.data.get('correo')
            newPwd = request.data.get('newPwd')
            pwd = request.data.get('pwd')
            if correo != '' and newPwd != '' and pwd != '' and validarPwd(correo, pwd):
                if(newPwd == pwd):
                    return Response({'message': 'La nueva contraseña no puede ser igual a la actual'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    print("validada")
                    usuaria = Usuaria.objects.get(correo=correo)
                    usuaria.pwd = newPwd
                    usuaria.save()
                    return Response({'message': 'Cambio de contraseña realizado ok'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Datos incorrectos'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message': 'Datos inválidos'}, status=status.HTTP_400_BAD_REQUEST)

# VALIDAR CONTRASEÑA
def validarPwd(correo, pwd):
    usuaria = Usuaria.objects.get(correo=correo)
    pwd_encriptada = usuaria.pwd
    if check_password(pwd, pwd_encriptada):
        print("true")
        return True
    else:
        print("false")
        return False

#==============================
# MÓDULO 3: FICHAS TÉCNICAS
#==============================

# SIMULADOR FT
class SimularFTAPIView(APIView):
    def get(self, request):
        cod_ft = request.GET.get('cod_ft')
        personas = int(request.GET.get('personas'))

        ft = get_object_or_404(Ft, cod_ft=cod_ft)
        detalle_ingredientes = DetalleIngrediente.objects.filter(ft_cod_ft=cod_ft)

        ingredientes_simulados = []
        costo_tot_sim = 0

        for detalle in detalle_ingredientes:
            nom_item = detalle.item_cod_item.nom_item
            unidad = detalle.item_cod_item.unidad_cod_unidad.unidad
            cantidad_sim = math.floor(detalle.cantidad * personas / ft.rendimiento)
            costo_det_sim = math.floor(detalle.costo_det * personas / ft.rendimiento)

            ingrediente_simulado = {
                'nom_item': nom_item,
                'unidad': unidad,
                'cantidad_sim': cantidad_sim,
                'costo_det_sim': costo_det_sim
            }

            ingredientes_simulados.append(ingrediente_simulado)
            costo_tot_sim += costo_det_sim

        ft_simulada = {
            'cod_ft': ft.cod_ft,
            'nom_ft': ft.nom_ft,
            'personas': personas,
            'costo_tot_sim': costo_tot_sim
        }

        response_data = {
            'ingredientes_simulados': ingredientes_simulados,
            'ft_simulada': ft_simulada
        }

        return Response(response_data)

#==============================   
# MÓDULO 4: PEDIDOS
#============================== 

# Revisar stock de artículos asociados a un ítem
def validar_disponibilidad_item(cod_item, cantidad):
    disponibilidad = Inventario.objects.filter(item_cod_item=cod_item).aggregate(stock_total=models.Sum('stock'))['stock_total']
    if disponibilidad is None:
        disponibilidad = 0

    if disponibilidad >= cantidad:
        return True
    else:
        return False

# Revisar stock de ítems asociados a una FT
def validar_stock_ft(cod_ft, cantidad):
    detalle_ingrediente_lista = DetalleIngrediente.objects.filter(ft_cod_ft=cod_ft)
    items_insuficientes = []

    for detalle_ingrediente in detalle_ingrediente_lista:
        cod_item = detalle_ingrediente.item_cod_item
        cantidad_requerida = math.floor(cantidad * detalle_ingrediente.cantidad / detalle_ingrediente.ft_cod_ft.rendimiento)
        print(cantidad_requerida)

        if not validar_disponibilidad_item(cod_item, cantidad_requerida):
            items_insuficientes.append(cod_item)

    return items_insuficientes

# Revisar stock para un pedido
def validar_stock_pedido(cod_pedido):
    detalle_pedido_lista = DetallePedido.objects.filter(pedido_cod_pedido=cod_pedido)
    items_no_disponibles = []

    for detalle_pedido in detalle_pedido_lista:
        if detalle_pedido.categoria == 2:
            cod_ft = detalle_pedido.ft_cod_ft
            cantidad = detalle_pedido.cantidad
            items_insuficientes = validar_stock_ft(cod_ft, cantidad)
            items_no_disponibles.extend(items_insuficientes)
        elif detalle_pedido.categoria == 1:
            cod_item = detalle_pedido.item_cod_item
            cantidad = detalle_pedido.cantidad
            if not validar_disponibilidad_item(cod_item, cantidad):
                items_no_disponibles.append(cod_item)

    return items_no_disponibles

# API de prueba para validar stock de pedido (solo prueba)
class ValidarStockPedidoAPIView(APIView):
    def get(self, request, cod_pedido):
        items_no_disponibles = validar_stock_pedido(cod_pedido)

        serializer = ItemSerializer(items_no_disponibles, many=True)

        return Response(serializer.data)

# Asignar usuaria a un pedido
def asignar_usuaria(id_usuaria, cod_pedido):
    try:
        usuaria = Usuaria.objects.get(id_usuaria=id_usuaria)
    except Usuaria.DoesNotExist:
        return False
    try:
        pedido = Pedido.objects.get(cod_pedido=cod_pedido)
    except Pedido.DoesNotExist:
        return False

    pedido.usuaria_id_usuaria = usuaria
    pedido.save()
    return True

# Actualizar el estado de un pedido
def actualizar_estado_pedido(cod_pedido, nuevo_estado):
    try:
        pedido = Pedido.objects.get(cod_pedido=cod_pedido)
    except Pedido.DoesNotExist:
        return False  
    try:
        estado = EstadoPedido.objects.get(cod_estado=nuevo_estado)
    except EstadoPedido.DoesNotExist:
        return False
    
    pedido.estado_pedido_cod_estado = estado
    pedido.save()
    return True

# ASIGNAR USUARIA A UN PEDIDO
class AsignarUsuariaAPIView(APIView):
    def patch(self, request):
        id_usuaria = request.data.get('id_usuaria')
        cod_pedido = request.data.get('cod_pedido')
        
        try:
            Usuaria.objects.get(id_usuaria=id_usuaria)
        except Usuaria.DoesNotExist:
            return Response("Usuaria no encontrada", status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = Pedido.objects.get(cod_pedido=cod_pedido)
        except Pedido.DoesNotExist:
            return Response("Pedido no encontrado", status=status.HTTP_400_BAD_REQUEST)

        if pedido.estado_pedido_cod_estado.cod_estado == 1:
            items_no_disponibles = validar_stock_pedido(cod_pedido)
            if not items_no_disponibles:
                asignar_usuaria(id_usuaria, cod_pedido)
                actualizar_estado_pedido(cod_pedido, 2)
                return Response("Pedido asignado", status=status.HTTP_200_OK)
            else:
                serializer = ItemSerializer(items_no_disponibles, many=True)
                return Response(serializer.data, status=status.HTTP_409_CONFLICT)
        elif pedido.estado_pedido_cod_estado.cod_estado in [2, 3, 4]:
            asignar_usuaria(id_usuaria, cod_pedido)
            return Response("Pedido asignado a una nueva usuaria", status=status.HTTP_200_OK)
        else:
            return Response("No es posible asignar una usuaria al pedido", status=status.HTTP_422_UNPROCESSABLE_ENTITY)

# ACTUALIZAR EL ESTADO DE UN PEDIDO
class ActualizarEstadoPedidoAPIView(APIView):
    def post(self, request):
        cod_pedido = request.data.get('cod_pedido')
        new_estado = request.data.get('new_estado')

        try:
            pedido = Pedido.objects.get(cod_pedido=cod_pedido)
        except Pedido.DoesNotExist:
            return Response("Pedido no encontrado", status=status.HTTP_400_BAD_REQUEST)

        try:
            estado = EstadoPedido.objects.get(cod_estado=new_estado)
        except EstadoPedido.DoesNotExist:
            return Response("Estado no encontrado", status=status.HTTP_400_BAD_REQUEST)

        pedido.estado_pedido_cod_estado = estado
        if int(new_estado) == 5:
            pedido.fecha_entrega = date.today()
        pedido.save()
        
        msje = "El nuevo estado es " + pedido.estado_pedido_cod_estado.estado
        return Response(msje, status=status.HTTP_200_OK)

#==============================   
# MÓDULO 6: INVENTARIO
#============================== 

# ACTUALIZAR INVENTARIO
def actualizarInventario(codigo_articulo, cantidad, tipo_registro):
    # tipo_registro: 1 = ENTRADA; 2 = SALIDA

    # Obtener artículo a actualizar
    articulo = Inventario.objects.get(cod_art = codigo_articulo)

    if tipo_registro == 1:
        # Obtener entradas del último periodo
        parametro = Parametro.objects.get(parametro = 'PERIODO_COSTO')
        fecha_ini = timezone.now() - timedelta(days = parametro.valor_param)
        entradas_periodo = Entrada.objects.filter(inventario_cod_art = codigo_articulo, fecha__gte = fecha_ini)
        # Calcular costo promedio ponderado de las entradas del último periodo
        total_costo_cantidad = 0
        total_cantidad = 0
        for entrada in entradas_periodo:
            total_costo_cantidad += entrada.costo_unit * entrada.cantidad
            total_cantidad += entrada.cantidad
        if total_cantidad != 0:
            costo_unit_promedio = total_costo_cantidad / total_cantidad
            # Actualizar costo del artículo
            articulo.costo_art = costo_unit_promedio
        # Actualizar total de entradas y stock
        articulo.tot_entradas += cantidad
        articulo.stock += cantidad
        articulo.save()
        return True

    elif tipo_registro == 2:
        if articulo.stock >= cantidad:    
            articulo.tot_salidas += cantidad
            articulo.stock -= cantidad
            articulo.save()
            return True
        else:
            return False
    else:
        return False
    
    