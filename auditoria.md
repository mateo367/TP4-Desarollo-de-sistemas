# **Parte 2 — Auditoría**

## **Sección 1 — Auditoría de los tests de la IA**

### **1.1. Evaluación de los ocho tests**

| Test | Clasificación | Justificación |
| ----- | ----- | ----- |
| test\_subtotal | Útil | Compara el subtotal con el precio del catálogo multiplicado por la cantidad. |
| test\_total\_funciona | Débil | Solo verifica que el resultado no sea None, sin comprobar los importes. |
| test\_total\_positivo | Débil | Comprueba que el total sea positivo, pero podría pasar aunque el cálculo fuera incorrecto. |
| test\_cupon\_egresados | Débil | Comprueba el descuento porcentual, pero no verifica el redondeo comercial ni los límites de vigencia. |
| test\_envio\_caba | Útil | Comprueba el costo de envío de CABA para un subtotal inferior al mínimo de envío gratis. |
| test\_descuento\_por\_cantidad | Útil | Comprueba el descuento del 10 % para seis prendas, pero no el límite de cinco. |
| test\_talle\_valido | Débil | No tiene un assert explícito; solo comprueba indirectamente que no se lance una excepción. |
| test\_no\_explota\_con\_varios\_productos | Inútil | Captura cualquier excepción y la ignora, por lo que puede pasar aunque el cálculo falle. |

### **1.2. Resultado de mutación**

**Comando ejecutado:**

python mutar.py \--tests test\_checkout\_ia.py

* Mutantes generados: 29\.
* Mutantes muertos: 17\.
* Mutantes sobrevivientes: 12\.
* Puntaje de mutación: 58,6 %.

La suite detectó 17 de los 29 cambios artificiales, pero no detectó los otros 12\. Entre los sobrevivientes hay modificaciones en los límites de cantidad, el descuento por prendas, la vigencia de cupones, el envío gratuito y el cálculo del total.

Por ejemplo, cambiar la condición de cantidad de \< 10 a \<= 10 puede provocar que se rechace una cantidad válida de diez prendas. También sobreviven cambios en la fórmula del total, lo que demuestra que los tests no comprueban suficientemente los importes exactos.

Algunos mutantes podrían ser equivalentes y no alterar el comportamiento observable. Por eso, deben analizarse antes de considerarlos errores reales.

### **1.3. ¿Por qué los tests pasan y no detectan las fallas?**

Que los ocho tests pasen no demuestra que el programa cumpla toda la especificación. Algunos verifican condiciones generales, como que el total sea positivo o que el resultado no sea None. Otros solo prueban un caso válido y no contemplan valores límite, entradas inválidas, redondeos ni errores de validación. Por ejemplo, test\_total\_positivo podría pasar aunque el envío o el descuento fueran incorrectos. Además, test\_no\_explota\_con\_varios\_productos oculta cualquier excepción porque la captura no comprueba que el cálculo haya terminado correctamente. El resultado de mutación confirma esta debilidad: la suite deja sobrevivir 12 mutantes de 29, incluidos cambios en límites y operaciones matemáticas importantes. Por lo tanto, una cobertura de código elevada no garantiza que los tests detecten errores de comportamiento.

## **Sección 2 — Hallazgos**

### **2.1. Resultado del linter**

**Comando ejecutado:**

python \-m ruff check checkout.py

Ruff encontró cinco problemas:

| Línea | Código | Hallazgo | Categoría | Severidad |
| ----- | ----- | ----- | ----- | ----- |
| 1 | F401 | Se importa json, pero no se utiliza. | Code smell | Baja |
| 50 | E722 | Se utiliza un except sin especificar el tipo de excepción. | Manejo de errores | Media |
| 57 | B008 | Se evalúa date.today() al definir el valor predeterminado. | Fechas | Media |
| 63 | E711 | Se compara con None mediante \!=. | Code smell | Baja |
| 102 | B008 | Se evalúa date.today() al definir el valor predeterminado. | Fechas | Media |

El problema de except es especialmente importante porque puede ocultar errores inesperados. Los valores predeterminados con date.today() también pueden provocar que las funciones utilicen una fecha anterior en llamadas posteriores, en lugar de consultar la fecha actual.

### **2.2. Fallas encontradas en checkout.py**

| Archivo y línea | Categoría | Regla | Cómo se encontró | Severidad |
| ----- | ----- | ----- | ----- | ----- |
| checkout.py:1 | Code smell | Calidad del código | Ruff detectó una importación sin utilizar. | Baja |
| checkout.py:13 | Alucinación | R6 | El cupón DEBUG100 no está definido en la especificación, pero se acepta. | Alta |
| checkout.py:34 | Strings | R2, R4 | El talle se modifica directamente en el diccionario recibido, incumpliendo la regla de no modificar el carrito. | Media |
| checkout.py:37 | Lógica y límites | R3 | La condición \< 10 rechaza la cantidad válida de diez prendas. | Alta |
| checkout.py:37 | Tipos | R3 | No se comprueba que la cantidad sea un entero; valores como 1.5 pueden aceptarse. | Alta |
| checkout.py:45-46 | Numéricos | R1, R7 | Los precios se representan como float en lugar de Decimal. | Alta |
| checkout.py:48-51 | Manejo de errores | R1, R3, R4 | Se captura cualquier excepción y se continúa, ocultando errores y pudiendo calcular un subtotal incompleto. | Alta |
| checkout.py:49 | Alucinación | R1 | Se utiliza el precio enviado por el cliente en vez de obtener siempre el precio del catálogo. | Alta |
| checkout.py:49 | Manejo de errores | R1 | Un producto inexistente puede provocar una excepción que se oculta, en lugar de lanzar CheckoutError con PRODUCTO\_INEXISTENTE. | Alta |
| checkout.py:54 | Numéricos | R7 | round() con valores float no garantiza el redondeo comercial solicitado. | Alta |
| checkout.py:57 | Fechas | R6 | date.today() como argumento predeterminado se evalúa al definir la función. | Media |
| checkout.py:60 | Lógica y límites | R5 | El descuento se aplica solo cuando hay más de cinco prendas, en lugar de cinco o más. | Alta |
| checkout.py:63 | Strings | R6 | Un cupón en minúsculas no se normaliza a mayúsculas, aunque la especificación no distingue mayúsculas de minúsculas. | Media |
| checkout.py:63-64 | Lógica y límites | R6 | Una cadena vacía o de espacios se procesa como cupón inexistente en lugar de equivaler a no usar cupón. | Media |
| checkout.py:68-71 | Fechas | R6 | El cupón vence también el 30/11/2026, aunque esa fecha debe ser válida inclusive. | Alta |
| checkout.py:72-74 | Numéricos | R6, R7 | El descuento porcentual se calcula con float y no garantiza redondeo comercial. | Alta |
| checkout.py:81-84 | Numéricos | R6, R7 | El descuento fijo se suma al descuento por cantidad en lugar de aplicar únicamente el mayor de ambos. | Alta |
| checkout.py:94 | Manejo de errores | R8 | ENVIOS.keys().join(...) es inválido; al construir el mensaje de una zona desconocida puede producirse un error en lugar de CheckoutError. | Media |
| checkout.py:96 | Lógica y límites | R8 | El envío gratuito se determina por el subtotal sin descontar, en lugar del subtotal con descuento aplicado. | Alta |
| checkout.py:102 | Fechas | R6 | Se repite el problema de date.today() como argumento predeterminado. | Media |
| checkout.py:105 | Lógica y límites | R4 | No se comprueba explícitamente si el carrito está vacío para lanzar CARRITO\_VACIO. | Alta |

### **2.3. Fallas encontradas en pedidos.py**

| Archivo y línea | Categoría | Regla | Cómo se encontró | Severidad |
| ----- | ----- | ----- | ----- | ----- |
| pedidos.py:45-56 | Efectos laterales | R10 | Se inserta el pedido y se confirma la transacción antes de calcular los importes. Si el cálculo falla, el pedido puede quedar guardado sin ser válido. | Alta |
| pedidos.py:47-51 | Strings | R10 | Se normaliza el email, la zona y el cupón, pero el cupón no se normaliza dentro de checkout.py y el talle se normaliza después de calcular los importes. | Media |
| pedidos.py:55-68 | Efectos laterales | R10 | No se confirma explícitamente la transacción después de actualizar los importes e insertar los ítems; otra conexión podría no ver el pedido completo. | Alta |
| pedidos.py:57-63 | Numéricos | R7, R10 | Los importes se convierten a float y se guardan en columnas REAL, lo que puede provocar pérdida de precisión decimal. | Alta |
| pedidos.py:66-68 | Alucinación | R1, R10 | El precio unitario se toma del ítem enviado por el cliente si incluye la clave precio, en lugar de usar siempre el catálogo. | Alta |
| pedidos.py:66-69 | Manejo de errores | R10 | Se usa acceso directo al catálogo y no se garantiza que los errores de productos inválidos se propaguen como CheckoutError sin dejar datos persistidos. | Alta |
| pedidos.py:80-83 | Numéricos | R7, R10 | Decimal(fila\["subtotal"\]) convierte un valor almacenado como REAL; no garantiza recuperar exactamente el importe original. | Alta |
| pedidos.py:106-108 | Seguridad | R10 | La consulta SQL se construye con interpolación del email, lo que permite inyección SQL. | Alta |

### **2.4. Fallas encontradas en api.py**

| Archivo y línea | Categoría | Regla | Cómo se encontró | Severidad |
| ----- | ----- | ----- | ----- | ----- |
| api.py:25 | Numéricos | R11 | json.dumps(..., default=float) convierte los importes decimales en números JSON en lugar de cadenas. | Alta |
| api.py:43-50 | Manejo de errores | R11 | Todos los errores se capturan como excepciones genéricas y se devuelven con HTTP 500, sin distinguir errores de negocio, JSON inválido ni datos incompletos. | Alta |
| api.py:33-41 | Manejo de errores | R11 | No se valida el formato de la fecha ni se convierte el texto recibido a date; una fecha inválida puede provocar errores inesperados. | Alta |
| api.py:33-41 | Tipos | R11 | No se comprueba que email, zona y carrito existan y tengan los tipos requeridos antes de procesarlos. | Alta |
| api.py:33-41 | Efectos laterales | R10, R11 | Si ocurre una excepción antes de con.close(), la conexión puede quedar abierta. | Media |
| api.py:43-50 | Manejo de errores | R11 | La respuesta de error no utiliza el formato requerido {"error": {"code": ..., "message": ...}}. | Alta |
| api.py:61-68 | Manejo de errores | R11 | Un pedido inexistente se devuelve como 200 con null, en vez de responder 404 con PEDIDO\_INEXISTENTE. | Alta |
| api.py:61-68 | Efectos laterales | R10, R11 | Si ocurre una excepción antes de con.close(), la conexión puede quedar abierta. | Media |

### **2.5. Resumen de fallas por severidad**

| Severidad | Fallas principales |
| ----- | ----- |
| Alta | Aceptación de cupones inexistentes, cantidades inválidas, precios enviados por el cliente, errores de cálculo, inyección SQL, persistencia parcial, pérdida de precisión, respuestas HTTP incorrectas y manejo incorrecto de errores. |
| Media | Normalización incompleta de cupones, fechas predeterminadas, errores al generar mensajes de zona inválida y posibles conexiones sin cerrar. |
| Baja | Importaciones sin utilizar y comparaciones de estilo. |

**Conclusión:** la suite de la IA no detecta muchas fallas porque comprueba pocos casos y no verifica todos los límites ni las condiciones de error. La auditoría del código muestra problemas tanto en los cálculos del checkout como en la persistencia y la API. Los errores más graves son los que pueden alterar los importes, aceptar datos inválidos, dejar pedidos incompletos o permitir inyección SQL. La cobertura de código y el hecho de que los tests pasen no garantizan que se cumpla el contrato. Por eso, las pruebas posteriores deben basarse en la especificación y cubrir casos válidos, inválidos, límites y errores de integración.

