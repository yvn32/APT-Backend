from rest_framework import serializers
from .models import Clienta, Comuna, Entrada, Inventario, Item, Pais, Parametro, Perfil, Proveedora, Region, RepLegal, Salida, Unidad, Usuaria

class ClientaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clienta
        fields = ('cod_clienta', 'rut_clienta', 'dv_clienta', 'tipo_clienta', 'nombre', 'apellido','nom_fantasia', 'rep_legal_cod_rep_legal', 'correo', 'tel', 'calle', 'numero', 'complemento', 'comuna_cod_comuna', 'pais_cod_pais', 'giro')
        read_only_fields = ('cod_clienta', )

class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ('cod_comuna', 'comuna', 'region_cod_region')
        read_only_fields = ('cod_comuna', 'comuna', 'region_cod_region', )

class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = ('id_entrada', 'inventario_cod_art', 'fecha', 'cantidad', 'costo_unit','descripcion')
        read_only_fields = ('id_entrada', 'fecha', )

class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = ('cod_art', 'nom_art', 'tot_entradas', 'tot_salidas', 'stock', 'costo_art','item_cod_item', 'proveedora_cod_proveedora')
        read_only_fields = ('cod_art', 'tot_entradas', 'tot_salidas', 'stock', 'costo_art', )

class ItemSerializar(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('cod_item', 'nom_item', 'categoria', 'unidad_cod_unidad', 'cant_item', 'costo_std')
        read_only_fields = ('cod_item', )

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ('cod_pais', 'pais', 'cod_alfa_3')
        read_only_fields = ('cod_pais', 'pais', 'cod_alfa_3', )

class ParametroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametro
        fields = ('codigo', 'parametro', 'valor_param')
        read_only_fields = ('codigo', 'parametro', )

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ('cod_perfil', 'perfil', 'mod1_acceso', 'mod2_acceso', 'mod3_acceso', 'mod4_acceso', 'mod5_acceso' , 'mod6_acceso')
        read_only_fields = ('cod_perfil', )

class ProveedoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedora
        fields = ('cod_proveedora', 'nom_proveedora', 'nom_contacto', 'correo', 'tel', 'calle', 'numero', 'complemento', 'comuna_cod_comuna', 'pais_cod_pais')
        read_only_fields = ('cod_proveedora', )

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('cod_region', 'region')
        read_only_fields = ('cod_region', 'region', )

class RepLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepLegal
        fields = ('cod_rep_legal', 'rut_rep_legal', 'dv_rep_legal', 'nombre', 'apellido', 'correo', 'tel')
        read_only_fields = ('cod_rep_legal', )

class SalidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salida
        fields = ('id_salida', 'inventario_cod_art', 'fecha', 'cantidad', 'descripcion')
        read_only_fields = ('id_salida', 'fecha', )

class UnidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidad
        fields = ('cod_unidad', 'unidad')
        read_only_fields = ('cod_unidad', 'unidad', )

class UsuariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuaria
        fields = ('id_usuaria', 'correo', 'pwd', 'nombre', 'apellido', 'logueada', 'perfil_cod_perfil')
        read_only_fields = ('id_usuaria', 'logueada', )

