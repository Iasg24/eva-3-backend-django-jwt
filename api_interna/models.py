from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    laboratorio = models.CharField(max_length=120)
    requiere_receta = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({self.laboratorio})"

    @property
    def precio_actual(self):
        # Obtiene el precio más reciente registrado
        ultimo = self.precios.order_by('-fecha_registro').first()
        return float(ultimo.valor) if ultimo else 0.0

class HistorialPrecio(models.Model):
    producto = models.ForeignKey(Producto, related_name='precios', on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Regla de negocio: El nuevo precio no puede variar en más de un 10% respecto al último
        ultimo_precio = self.producto.precios.order_by('-fecha_registro').first()
        if ultimo_precio and ultimo_precio.id != self.id:
            precio_base = float(ultimo_precio.valor)
            limite_inferior = precio_base * 0.90
            limite_superior = precio_base * 1.10
            valor_nuevo = float(self.valor)

            if valor_nuevo < limite_inferior or valor_nuevo > limite_superior:
                raise ValidationError(
                    f"El nuevo precio ({valor_nuevo}) no puede variar en más del 10% respecto al anterior ({precio_base}). "
                    f"Rango permitido: [{limite_inferior:.2f} - {limite_superior:.2f}]"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} - ${self.valor} ({self.fecha_registro.strftime('%d/%m/%Y %H:%M')})"