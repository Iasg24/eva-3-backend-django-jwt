# Declaración de Uso de Inteligencia Artificial (USO_IA.md)

**Asignatura:** Desarrollo Backend / Programación Web  
**Estudiante:** Ignacio Sánchez Godoy  
**Proyecto:** API Interna de Catálogo Farmacéutico (Evaluación 3)  
**Herramienta IA utilizada:** Modelo LLM (Gemini)

---

## 1. Propósito del Uso de la IA
Durante el desarrollo del proyecto se utilizó la inteligencia artificial como **asistente técnico, depurador de errores y consultor de arquitectura de software**. La intervención de la herramienta se enfocó en optimizar el flujo de trabajo, estructurar buenas prácticas bajo Django REST Framework (DRF) y acelerar la resolución de problemas específicos del entorno de ejecución (Linux / MariaDB).

---

## 2. Áreas Específicas de Asistencia

### A. Diseño y Modelado de Datos
* **Regla de negocio del 10%:** Asistencia en la formulación de la lógica en el método `clean()` del modelo `HistorialPrecio`, asegurando que la comparación contra el último precio registrado impidiera variaciones mayores al 10% (al alza o a la baja).
* **Campos automáticos y trazabilidad:** Asignación del usuario creador autenticado (`usuario_creacion`) a través de la sobreescritura de `perform_create()` en el ViewSet.

### B. Vistas, Serializadores y Throttling
* **Diseño del ViewSet:** Implementación de `ProductoViewSet` heredando de `ModelViewSet` para cumplir con las operaciones CRUD estándar.
* **Separación de Serializadores:** Configuración de `get_serializer_class()` para mostrar una vista ligera en listados (`ProductoListSerializer` con solo el precio actual) y una vista detallada con historial acotado (`ProductoDetailSerializer`).
* **Seguridad y Throttling:** Configuración global de `DEFAULT_THROTTLE_CLASSES` y `DEFAULT_THROTTLE_RATES` (`AnonRateThrottle` y `UserRateThrottle`) en `settings.py`.

### C. Resolución de Problemas y Troubleshooting (Debugging)
* **Conexión a MariaDB por Socket UNIX:** Resolución del error `OperationalError: (2002, "Can't connect to server on '127.0.0.1' (115)")`, ajustando la configuración de base de datos para utilizar el socket local `/run/mysqld/mysqld.sock`.
* **Depuración de Autenticación JWT en Postman:**
  * Corrección del error `415 Unsupported Media Type` por envío de payload en texto plano en lugar de `application/json`.
  * Corrección del error `403 Forbidden` (`Authentication credentials were not provided`) mediante la declaración explícita de `authentication_classes = [JWTAuthentication]` en la vista y la correcta estructuración del encabezado `Authorization: Bearer <token>`.
  * Ajuste del tiempo de vida del token en `SIMPLE_JWT` (`ACCESS_TOKEN_LIFETIME = timedelta(days=1)`) para evitar vencimientos prematuros durante las pruebas manuales.

---

## 3. Prompts Representativos Utilizados

A continuación se detallan ejemplos de interacciones representativas mantenidas con la herramienta:

1. **Consulta de Arquitectura / Vistas:**
   > *"Necesito implementar el ModelViewSet en DRF para el catálogo con filtrado por nombre y ordenamiento por precio o nombre, además de un endpoint personalizado para actualizar el precio respetando la regla del 10%."*
   
2. **Consulta de Error de Conexión:**
   > *"Al correr `python manage.py check` me sale el error `OperationalError: (2002, "Can't connect to server on '127.0.0.1' (115)")`. Estoy en Linux con MariaDB."*

3. **Consulta de Autenticación:**
   > *"Tengo configurado el token de JWT pero al hacer el POST a `/api/productos/` en Postman me responde `403 Forbidden: Authentication credentials were not provided`."*

---

## 4. Validación Crítica y Control del Estudiante
Todo el código y las recomendaciones entregadas por la IA fueron revisados, analizados y probados manualmente:
* Se verificó la sintaxis y compatibilidad con Python y mysql.
* Se validaron manualmente los endpoints mediante Postman y la consola de Django.
* Se verificó que las migraciones (`makemigrations` / `migrate`) generaran las tablas correctas en la base de datos `catalogo_db`.
* La autoría intelectual de la integración, estructuración final del proyecto y ejecución de pruebas corresponde al estudiante.

parte 2 aprendizaje del proyecto

Cómo viaja realmente el JWT: Al principio me tiraba error 403 todo el rato en Postman diciendo que no enviaba credenciales. Ahí aprendí que no sirve pegar el token suelto: tiene que llevar la palabra Bearer  con un espacio adelante en la cabecera Authorization. También entendí que el token access dura poco por seguridad y que si expira en medio de las pruebas, te rechaza la petición aunque el código esté bien.

Separar los Serializers: Me quedó claro que no tiene sentido mandar todo el historial de precios cuando solo quieres listar productos en una tabla. Aprendí a usar un serializador liviano para la lista general (que solo muestre el precio actual) y otro más completo para ver el detalle de un producto específico con sus precios anteriores.

Proteger los datos con variables de entorno: Aprendí a no dejar las contraseñas de la base de datos ni la SECRET_KEY escritas directamente en el archivo settings.py. Es mucho más seguro dejarlas en un archivo .env aparte y agregar ese archivo al .gitignore para no subir claves a internet.

Validar reglas en el modelo: Entendí que la regla del 10% conviene dejarla en el método clean() del modelo. De esa forma, si alguien intenta meter un precio con una variación mayor al 10% desde la API o desde cualquier otra parte, la base de datos y Django lo bloquean de inmediato.