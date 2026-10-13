from rest_framework import serializers
from .models import Producto, HistorialPrecio

class HistorialPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialPrecio
        fields = ['id', 'valor', 'fecha_registro']

# Serializer para listar todos los productos (muestra solo precio_actual)
class ProductoListSerializer(serializers.ModelSerializer):
    precio_actual = serializers.ReadOnlyField()
    usuario_creacion_nombre = serializers.ReadOnlyField(source='usuario_creacion.username')

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'laboratorio',
            'requiere_receta',
            'fecha_creacion',
            'usuario_creacion',
            'usuario_creacion_nombre',
            'precio_actual'
        ]
        read_only_fields = ['usuario_creacion']

# Serializer para el detalle (con historial dinámico)
class ProductoDetailSerializer(serializers.ModelSerializer):
    precio_actual = serializers.ReadOnlyField()
    usuario_creacion_nombre = serializers.ReadOnlyField(source='usuario_creacion.username')
    precios_historicos = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'laboratorio',
            'requiere_receta',
            'fecha_creacion',
            'usuario_creacion',
            'usuario_creacion_nombre',
            'precio_actual',
            'precios_historicos'
        ]
        read_only_fields = ['usuario_creacion']

    def get_precios_historicos(self, obj):
        request = self.context.get('request')
        limite = 3  # Por defecto muestra los últimos 3 precios

        if request and 'cantidad_precios' in request.query_params:
            try:
                limite = int(request.query_params.get('cantidad_precios'))
            except (ValueError, TypeError):
                limite = 3

        precios = obj.precios.order_by('-fecha_registro')[:limite]
        return HistorialPrecioSerializer(precios, many=True).data