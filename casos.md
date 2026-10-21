# Parte 1

Los casos se elaboraron usando únicamente ESPECIFICACION.md, sin analizar el código.

## R1 — Catálogo y precios

Particiones:

* Válidas: buzo, remera, campera.
* Inválidas: productos inexistentes o nombres con mayúsculas o espacios.
* Límite: hay tres productos válidos.

| Entrada | Resultado esperado |
| ----- | ----- |
| buzo | Precio \$24.999,90 |
| remera | Precio \$11.999,50 |
| campera | Precio \$47.999,99 |
| gorra | PRODUCTO\_INEXISTENTE |
| Buzo | PRODUCTO\_INEXISTENTE |
| buzo con precio propio de \$1 | Se ignora el precio enviado. |

## R2 — Talles

Particiones:

* Válidas: XS, S, M, L, XL, XXL; admite minúsculas y espacios exteriores.
* Inválidas: talles inexistentes, vacíos o de tipo incorrecto.
* Límites: XS y XXL son los extremos válidos.

| Entrada | Resultado esperado |
| ----- | ----- |
| XS, XXL | Aceptados |
| m, M | Aceptados |
| XXXL, "", None | TALLE\_INVALIDO |

## R3 — Cantidad

Particiones:

* Válidas: enteros del 1 al 10 inclusive.
* Inválidas: valores menores que 1, mayores que 10, decimales, cadenas y booleanos.
* Límites: 1 y 10 válidos; 0 y 11 inválidos.

| Entrada | Resultado esperado |
| ----- | ----- |
| 1, 10 | Aceptados |
| 0, 11, \-1, 1.5, "2", True | CANTIDAD\_INVALIDA |

## R4 — Carrito

Particiones:

* Válidas: listas con uno o más ítems válidos.
* Inválidas: listas vacías.
* Límite: un ítem es el mínimo válido.

| Entrada | Resultado esperado |
| ----- | ----- |
| Un buzo válido | Compra aceptada |
| \[\] | CARRITO\_VACIO |
| Carrito con claves adicionales | Las claves se ignoran |
| Carrito antes y después del cálculo | El contenido permanece igual |

## R5 — Descuento por cantidad

Particiones:

* Sin descuento: menos de 5 prendas.
* Con descuento: 5 prendas o más.
* Límites: 4 prendas no reciben descuento; 5 reciben el 10 %.

| Entrada | Resultado esperado |
| ----- | ----- |
| 4 buzos | Descuento \$0,00 |
| 5 buzos | Descuento del 10 % |
| Dos ítems con cantidades 2 y 3 | Descuento del 10 % sobre el subtotal conjunto |

## R6 — Cupones

Particiones:

* Válidas: EGRESADOS2026 y BIENVENIDA, sin distinguir mayúsculas y admitiendo espacios exteriores.
* Sin cupón: None, "" o espacios.
* Inválidas: cupón desconocido, vencido o que no alcanza el mínimo.
* Límites: EGRESADOS2026 es válido hasta el 30/11/2026; BIENVENIDA requiere \$20.000.

| Entrada | Resultado esperado |
| ----- | ----- |
| EGRESADOS2026, subtotal \$11.999,50, fecha 30/11/2026 | Descuento \$1.799,93 |
| EGRESADOS2026, fecha 01/12/2026 | CUPON\_VENCIDO |
| BIENVENIDA, subtotal \$20.000 | Descuento \$3.000 |
| BIENVENIDA, subtotal \$19.999,99 | CUPON\_MINIMO\_NO\_ALCANZADO |
| Cupón OTRO2026 | CUPON\_INVALIDO |
| Cupón y descuento por cantidad | Se aplica el mayor, sin acumularlos |
| Cupón vacío o None | No se aplica descuento por cupón |

## R7 — Dinero y redondeo

Particiones:

* Válidas: importes calculados con Decimal.
* Inválidas: uso de float para los importes.
* Límite: los porcentajes se redondean al centavo comercial.

| Entrada | Resultado esperado |
| ----- | ----- |
| 15 % de \$11.999,50 | Decimal("1799.93") |
| Precio de un buzo | Decimal("24999.90") |

## R8 — Envío

Particiones:

* Válidas: CABA, GBA, INTERIOR y RETIRO; admite minúsculas y espacios exteriores.
* Inválidas: zonas desconocidas.
* Límite: envío gratis con subtotal descontado de \$60.000 o más.

| Entrada | Resultado esperado |
| ----- | ----- |
| CABA | \$2.500 |
| GBA | \$4.000 |
| INTERIOR | \$6.500 |
| RETIRO | \$0 |
| caba | \$2.500 |
| PATAGONIA | ZONA\_INVALIDA |
| Subtotal \$59.999,99 | Se cobra envío |
| Subtotal \$60.000 | Envío gratis |

## R9 — Total y orden de validación

Particiones:

* Válidas: compras con carrito, ítems y zona válidos.
* Inválidas: compras con datos incorrectos.
* Orden: carrito, producto, talle, cantidad, cupón y zona.

| Entrada | Resultado esperado |
| ----- | ----- |
| 2 buzos, zona CABA, sin cupón | Total \$52.499,80 |
| Carrito vacío y zona inválida | CARRITO\_VACIO |
| Producto y talle inválidos | PRODUCTO\_INEXISTENTE |
| Talle y cantidad inválidos | TALLE\_INVALIDO |
| Cupón y zona inválidos | CUPON\_INVALIDO |
| Zona RETIRO | Total \= subtotal − descuento |

## R10 — Persistencia

Particiones:

* Válidas: pedidos correctos, guardados y recuperados desde SQLite.
* Inválidas: pedidos con errores de checkout o identificadores inexistentes.
* Límites: no debe quedar ningún dato guardado si falla el checkout.

| Entrada | Resultado esperado |
| ----- | ----- |
| Guardar un pedido válido | Se guarda con sus ítems y se puede recuperar desde otra conexión |
| Guardar un pedido inválido | Se propaga CheckoutError y no se guarda nada |
| Recuperar un ID inexistente | None |
| Consultar por email con mayúsculas o espacios | Devuelve los pedidos correspondientes |
| Email con texto SQL como entrada | No altera la consulta |
| Guardar montos y recuperarlos | Los valores Decimal se conservan sin pérdidas |
| Consultar pedidos de un email | Se ordenan del más reciente al más antiguo |
| Enviar precio propio en un ítem | Se guarda el precio del catálogo |

## R11 — API HTTP

Particiones:

* Válidas: creación de pedidos por POST y consulta por GET.
* Inválidas: JSON incorrecto, datos incompletos, fecha inválida, errores de negocio, pedido inexistente y ruta desconocida.
* Límites: los importes deben enviarse como texto y ningún error debe producir un HTTP 500\.

| Entrada | Resultado esperado |
| ----- | ----- |
| POST con pedido válido | HTTP 201 y montos como texto |
| GET de un pedido existente | HTTP 200 y pedido completo |
| JSON malformado | HTTP 400, JSON\_INVALIDO |
| Falta email, zona o carrito, o tienen tipo incorrecto | HTTP 400, DATOS\_INCOMPLETOS |
| Fecha con formato incorrecto | HTTP 400, FECHA\_INVALIDA |
| Error de checkout | HTTP 422 y código correspondiente |
| GET de pedido inexistente | HTTP 404, PEDIDO\_INEXISTENTE |
| Ruta inexistente | HTTP 404, RUTA\_INEXISTENTE |
| Cualquier error | Nunca HTTP 500 |

