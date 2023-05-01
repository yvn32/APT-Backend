# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

#==============================   
# FUNCIONES AUXILIARES
#============================== 

def validar_positivo(valor):
    if valor <= 0:
        raise ValidationError('El valor ingresado debe ser mayor que cero')

#==============================   
# MODELOS
#============================== 

class Clienta(models.Model):
    cod_clienta = models.AutoField(primary_key=True)
    rut_clienta = models.BigIntegerField(unique=True)
    dv_clienta = models.CharField(max_length=1)
    tipo_clienta = models.IntegerField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    nom_fantasia = models.CharField(max_length=100, blank=True, null=True)
    rep_legal_cod_rep_legal = models.ForeignKey('RepLegal', models.DO_NOTHING, db_column='rep_legal_cod_rep_legal', blank=True, null=True)
    correo = models.CharField(max_length=100)
    tel = models.BigIntegerField()
    calle = models.CharField(max_length=200)
    numero = models.IntegerField()
    complemento = models.CharField(max_length=10, blank=True, null=True)
    comuna_cod_comuna = models.ForeignKey('Comuna', models.DO_NOTHING, db_column='comuna_cod_comuna')
    pais_cod_pais = models.ForeignKey('Pais', models.DO_NOTHING, db_column='pais_cod_pais')
    giro = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clienta'

class Comuna(models.Model):
    cod_comuna = models.IntegerField(primary_key=True)
    comuna = models.CharField(max_length=50)
    region_cod_region = models.ForeignKey('Region', models.DO_NOTHING, db_column='region_cod_region')

    class Meta:
        managed = False
        db_table = 'comuna'

class DetalleIngrediente(models.Model):
    cantidad = models.IntegerField()
    item_cod_item = models.ForeignKey('Item', models.DO_NOTHING, db_column='item_cod_item')
    ft_cod_ft = models.ForeignKey('Ft', models.DO_NOTHING, db_column='ft_cod_ft')

    class Meta:
        managed = False
        db_table = 'detalle_ingrediente'

class DetallePedido(models.Model):
    id_registro = models.AutoField(primary_key=True)
    pedido_cod_pedido = models.ForeignKey('Pedido', models.DO_NOTHING, db_column='pedido_cod_pedido')
    categoria = models.IntegerField()
    item_cod_item = models.ForeignKey('Item', models.DO_NOTHING, db_column='item_cod_item')
    ft_cod_ft = models.ForeignKey('Ft', models.DO_NOTHING, db_column='ft_cod_ft')
    cantidad = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'detalle_pedido'

class DetallePreparacion(models.Model):
    instruccion = models.CharField(max_length=300)
    ft_cod_ft = models.ForeignKey('Ft', models.DO_NOTHING, db_column='ft_cod_ft')

    class Meta:
        managed = False
        db_table = 'detalle_preparacion'

class Entrada(models.Model):
    id_entrada = models.AutoField(primary_key=True)
    inventario_cod_art = models.ForeignKey('Inventario', models.DO_NOTHING, db_column='inventario_cod_art')
    fecha = models.DateField(auto_now_add=True)
    cantidad = models.IntegerField()
    costo_unit = models.BigIntegerField(validators=[validar_positivo])
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entrada'

class EstadoPedido(models.Model):
    cod_estado = models.IntegerField(primary_key=True)
    estado = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'estado_pedido'

class Ft(models.Model):
    cod_ft = models.AutoField(primary_key=True)
    nom_ft = models.CharField(max_length=100)
    rendimiento = models.IntegerField()
    observacion = models.CharField(max_length=500, blank=True, null=True)
    costo_tot = models.BigIntegerField()
    img_ft = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'ft'

class Inventario(models.Model):
    cod_art = models.AutoField(primary_key=True)
    nom_art = models.CharField(max_length=100)
    tot_entradas = models.IntegerField(default=0)
    tot_salidas = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    costo_art = models.BigIntegerField(default=0)
    item_cod_item = models.ForeignKey('Item', models.DO_NOTHING, db_column='item_cod_item')
    proveedora_cod_proveedora = models.ForeignKey('Proveedora', models.DO_NOTHING, db_column='proveedora_cod_proveedora')

    class Meta:
        managed = False
        db_table = 'inventario'
        unique_together = ('nom_art', 'item_cod_item', 'proveedora_cod_proveedora')

class Item(models.Model):
    cod_item = models.AutoField(primary_key=True)
    nom_item = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=30)
    unidad_cod_unidad = models.ForeignKey('Unidad', models.DO_NOTHING, db_column='unidad_cod_unidad')
    cant_item = models.IntegerField(validators=[validar_positivo])
    costo_std = models.BigIntegerField(validators=[validar_positivo])

    class Meta:
        managed = False
        db_table = 'item'

class Pais(models.Model):
    cod_pais = models.IntegerField(primary_key=True)
    pais = models.CharField(max_length=100)
    cod_alfa_3 = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'pais'

class Parametro(models.Model):
    codigo = models.IntegerField(primary_key=True)
    parametro = models.CharField(max_length=30)
    valor_param = models.IntegerField(validators=[validar_positivo])

    class Meta:
        managed = False
        db_table = 'parametro'

class Pedido(models.Model):
    cod_pedido = models.AutoField(primary_key=True)
    fecha_registro = models.DateField()
    fecha_compromiso = models.DateField()
    costo_tot = models.BigIntegerField()
    margen = models.IntegerField()
    precio = models.BigIntegerField()
    clienta_cod_clienta = models.ForeignKey(Clienta, models.DO_NOTHING, db_column='clienta_cod_clienta')
    estado_pedido_cod_estado = models.ForeignKey(EstadoPedido, models.DO_NOTHING, db_column='estado_pedido_cod_estado')
    fecha_entrega = models.DateField()
    usuaria_id_usuaria = models.ForeignKey('Usuaria', models.DO_NOTHING, db_column='usuaria_id_usuaria')

    class Meta:
        managed = False
        db_table = 'pedido'

class Perfil(models.Model):
    cod_perfil = models.SmallAutoField(primary_key=True)
    perfil = models.CharField(max_length=50)
    mod1_acceso = models.IntegerField()
    mod2_acceso = models.IntegerField()
    mod3_acceso = models.IntegerField()
    mod4_acceso = models.IntegerField()
    mod5_acceso = models.IntegerField()
    mod6_acceso = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'perfil'

class Proveedora(models.Model):
    cod_proveedora = models.AutoField(primary_key=True)
    nom_proveedora = models.CharField(max_length=100, unique=True)
    nom_contacto = models.CharField(max_length=50)
    correo = models.CharField(max_length=100)
    tel = models.BigIntegerField()
    calle = models.CharField(max_length=100)
    numero = models.IntegerField()
    complemento = models.CharField(max_length=10, blank=True, null=True)
    comuna_cod_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='comuna_cod_comuna')
    pais_cod_pais = models.ForeignKey(Pais, models.DO_NOTHING, db_column='pais_cod_pais')

    class Meta:
        managed = False
        db_table = 'proveedora'

class Region(models.Model):
    cod_region = models.IntegerField(primary_key=True)
    region = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'region'

class RepLegal(models.Model):
    cod_rep_legal = models.AutoField(primary_key=True)
    rut_rep_legal = models.BigIntegerField(unique=True)
    dv_rep_legal = models.CharField(max_length=1)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.CharField(max_length=100)
    tel = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'rep_legal'

class Salida(models.Model):
    id_salida = models.AutoField(primary_key=True)
    inventario_cod_art = models.ForeignKey(Inventario, models.DO_NOTHING, db_column='inventario_cod_art')
    fecha = models.DateField(auto_now_add=True)
    cantidad = models.IntegerField(validators=[validar_positivo])
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salida'

class Unidad(models.Model):
    cod_unidad = models.IntegerField(primary_key=True)
    unidad = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'unidad'

class Usuaria(models.Model):
    id_usuaria = models.AutoField(primary_key=True)
    correo = models.CharField(max_length=100, unique=True)
    pwd = models.CharField(max_length=100)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    logueada = models.IntegerField(default=0)
    perfil_cod_perfil = models.ForeignKey(Perfil, models.DO_NOTHING, db_column='perfil_cod_perfil')

    class Meta:
        managed = False
        db_table = 'usuaria'
    
    def save(self, *args, **kwargs):
        # Encriptar contraseña antes de guardarla en la base de datos
        self.pwd = make_password(self.pwd)
        super().save(*args, **kwargs)

