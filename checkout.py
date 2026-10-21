import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class CheckoutError(Exception):
    def __init__(self, code, mensaje):
        super().__init__(mensaje)
        self.code = code
        self.mensaje = mensaje


CATALOGO = {
    "buzo": 24999.90,
    "remera": 11999.50,
    "campera": 47999.99,
}

TALLES = ["XS", "S", "M", "L", "XL", "XXL"]

CUPONES = {
    "EGRESADOS2026": {"tipo": "porcentaje", "valor": 0.15, "vence": date(2026, 11, 30)},
    "BIENVENIDA": {"tipo": "fijo", "valor": 3000, "minimo": 20000},
}

ENVIOS = {
    "CABA": 2500,
    "GBA": 4000,
    "INTERIOR": 6500,
    "RETIRO": 0,
}

CENTAVO = Decimal("0.01")


def validar_item(item):
    talle = item.get("talle")
    if not isinstance(talle, str) or talle.strip().upper() not in TALLES:
         CheckoutError("TALLE_INVALIDO", f"Talle inválido: {talle!r}")

    if item["talle"] not in TALLES:
        raise CheckoutError("TALLE_INVALIDO", f"Talle inválido: {item['talle']}")

    cantidad = item.get("cantidad")
    if (
        isinstance(cantidad, bool)
        or not isinstance(cantidad, int)
        or not 1 <= cantidad <= 10
    ): raise CheckoutError("CANTIDAD_INVALIDA", "La cantidad debe estar entre 1 y 10")


def calcular_subtotal(carrito):
    subtotal = Decimal("0.00")

    for item in carrito:
        validar_item(item)

        producto = item["producto"]

        if producto not in CATALOGO:
            raise CheckoutError(
                "PRODUCTO_INEXISTENTE",
                f"Producto inexistente: {producto}"
            )

        precio = Decimal(str(CATALOGO[producto]))
        cantidad = item["cantidad"]

        subtotal += precio * cantidad

    return subtotal.quantize(Decimal("0.01"))






def calcular_descuento(
    subtotal,
    cantidad_prendas,
    cupon=None,
    fecha=None
):
    subtotal = Decimal(str(subtotal))
    descuento = Decimal("0.00")

    codigo = (cupon or "").strip().upper()

    if fecha is None:
        from datetime import date
        fecha = date.today()

    # Sin cupón: aplicar descuento por cantidad.
    if not codigo:
        if cantidad_prendas >= 5:
            descuento = subtotal * Decimal("0.10")

        return descuento.quantize(
            CENTAVO,
            rounding=ROUND_HALF_UP
        )

    if codigo not in CUPONES:
        raise CheckoutError(
            "CUPON_INVALIDO",
            "El cupón no existe"
        )

    datos = CUPONES[codigo]

    if datos["tipo"] == "porcentaje":
        if fecha > datos["vence"]:
            raise CheckoutError(
                "CUPON_VENCIDO",
                "El cupón está vencido"
            )

        descuento = subtotal * Decimal(str(datos["valor"]))

    elif datos["tipo"] == "fijo":
        minimo = Decimal(str(datos["minimo"]))

        if subtotal < minimo:
            raise CheckoutError(
                "CUPON_MINIMO_NO_ALCANZADO",
                "El subtotal no alcanza el mínimo requerido"
            )

        descuento = Decimal(str(datos["valor"]))

    else:
        raise CheckoutError(
            "CUPON_INVALIDO",
            "Tipo de cupón inválido"
        )

    return descuento.quantize(
        CENTAVO,
        rounding=ROUND_HALF_UP
    )




def calcular_envio(subtotal, zona):
    zona = zona.strip().upper()

    if zona not in ENVIOS:
        opciones = ", ".join(ENVIOS.keys())

        raise CheckoutError(
            "ZONA_INVALIDA",
            f"Zona inválida. Opciones: {opciones}"
        )

    subtotal = Decimal(str(subtotal))

    if subtotal >= Decimal("60000.00"):
        return Decimal("0.00")

    return Decimal(str(ENVIOS[zona])).quantize(
        Decimal("0.01")
    )



def calcular_total(carrito, zona, cupon=None, fecha=None):
    if not carrito:
        raise CheckoutError(
            "CARRITO_VACIO",
            "El carrito está vacío"
        )
        
    carrito_normalizado = []

    for item in carrito:
        copia = item.copy()
        copia["talle"] = copia["talle"].strip().upper()
        carrito_normalizado.append(copia)

    subtotal = calcular_subtotal(carrito_normalizado)

    cantidad_prendas = sum(
        item["cantidad"] for item in carrito_normalizado
    )

    descuento = calcular_descuento(
        subtotal,
        cantidad_prendas,
        cupon,
        fecha
    )

    envio = calcular_envio(subtotal, zona)

    total = (subtotal - descuento + envio).quantize(
        Decimal("0.01")
    )

    return {
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "descuento": descuento.quantize(Decimal("0.01")),
        "envio": envio.quantize(Decimal("0.01")),
        "total": total,
    }
