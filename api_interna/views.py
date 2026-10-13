from decimal import Decimal
from django.db.models import Max
from django.core.exceptions import ValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Producto, HistorialPrecio
from .serializers import (
    ProductoListSerializer,
    ProductoDetailSerializer,
    HistorialPrecioSerializer
)

class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD sobre Producto.
    Aplica autenticación obligatoria y throttling configurado en settings.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # En la vista de detalle muestra los últimos precios; en lista solo el actual
        if self.action == 'retrieve':
            return ProductoDetailSerializer
        return ProductoListSerializer

    def get_queryset(self):
        # Anotamos el último precio registrado para permitir el ordenamiento por precio
        queryset = Producto.objects.annotate(
            ultimo_precio=Max('precios__valor')
        )

        # Regla de filtrado: query param ?nombre= (coincidencia parcial)
        nombre = self.request.query_params.get('nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        # Regla de ordenamiento: query param ?ordenar=nombre o ?ordenar=precio
        ordenar = self.request.query_params.get('ordenar')
        es_desc = self.request.query_params.get('desc')

        if ordenar == 'nombre':
            campo = '-nombre' if es_desc else 'nombre'
            queryset = queryset.order_by(campo)
        elif ordenar == 'precio':
            campo = '-ultimo_precio' if es_desc else 'ultimo_precio'
            queryset = queryset.order_by(campo)

        return queryset

    def perform_create(self, serializer):
        # Asigna automáticamente al usuario logueado como creador
        producto = serializer.save(usuario_creacion=self.request.user)

        # Si en el cuerpo de la petición viene un precio inicial, lo registra
        precio_inicial = self.request.data.get('precio')
        if precio_inicial is not None:
            HistorialPrecio.objects.create(
                producto=producto,
                valor=Decimal(str(precio_inicial))
            )

    @action(detail=True, methods=['post'], url_path='actualizar-precio')
    def actualizar_precio(self, request, pk=None):
        """
        Endpoint personalizado para agregar un nuevo precio al historial.
        Ejecuta la validación del 10% definida en el modelo.
        """
        producto = self.get_object()
        nuevo_valor = request.data.get('valor')

        if not nuevo_valor:
            return Response(
                {'error': 'Debe proporcionar el campo "valor" para el nuevo precio.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            nuevo_precio = HistorialPrecio(
                producto=producto,
                valor=Decimal(str(nuevo_valor))
            )
            nuevo_precio.save() # Dispara clean() con la regla del 10%
            return Response(
                HistorialPrecioSerializer(nuevo_precio).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)