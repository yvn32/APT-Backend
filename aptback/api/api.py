from .models import Clienta, Comuna, Entrada, Inventario, Item, Pais, Parametro, Perfil, Proveedora, Region, RepLegal, Salida,Unidad, Usuaria
from rest_framework import viewsets, permissions, status
from .serializers import ClientaSerializer, ComunaSerializer, EntradaSerializer, InventarioSerializer, ItemSerializar, PaisSerializer, ParametroSerializer, PerfilSerializer, ProveedoraSerializer, RegionSerializer, RepLegalSerializer, SalidaSerializer, UnidadSerializer, UsuariaSerializer
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from functools import partial
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView

class ClientaViewSet(viewsets.ModelViewSet):
    queryset = Clienta.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientaSerializer

class ComunaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comuna.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ComunaSerializer

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

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = InventarioSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ItemSerializar

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
    
    