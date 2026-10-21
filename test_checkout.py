
from datetime import date
from decimal import Decimal

import pytest

from checkout import (
    CheckoutError,
    calcular_descuento,
    calcular_envio,
    calcular_subtotal,
    calcular_total,
    validar_item,
)


HOY_VIGENTE = date(2026, 10, 1)


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def codigo_de_error(funcion, *args):
    with pytest.raises(CheckoutError) as error:
        funcion(*args)
    return error.value.code


def test_cantidad_cero_es_invalida():
    assert codigo_de_error(validar_item, item(cantidad=0)) == "CANTIDAD_INVALIDA"


def test_cantidad_diez_es_valida():
    validar_item(item(cantidad=10))


def test_cantidad_once_es_invalida():
    with pytest.raises(CheckoutError):
        validar_item(item(cantidad=11))


def test_cantidad_decimal_es_invalida():
    assert codigo_de_error(
        validar_item, item(cantidad=1.5)
    ) == "CANTIDAD_INVALIDA"


def test_producto_inexistente_lanza_error():
    assert codigo_de_error(
        calcular_subtotal, [item(producto="gorra")]
    ) == "PRODUCTO_INEXISTENTE"


def test_talle_normaliza_sin_modificar_carrito():
    carrito = [item(talle=" m ")]
    original = [dict(carrito[0])]

    resultado = calcular_total(carrito, " CABA ")

    assert carrito == original
    assert resultado["subtotal"] == Decimal("24999.90")


def test_subtotal_usa_decimal_y_precio_de_catalogo():
    resultado = calcular_subtotal([
        item(precio=Decimal("1.00"))
    ])

    assert resultado == Decimal("24999.90")
    assert isinstance(resultado, Decimal)


def test_cinco_prendas_tienen_descuento():
    descuento = calcular_descuento(
        Decimal("10000.00"), 5, fecha=HOY_VIGENTE
    )

    assert descuento == Decimal("1000.00")


def test_cupon_egresados_redondea_al_centavo():
    descuento = calcular_descuento(
        Decimal("11999.50"), 1, " EGRESADOS2026 ", HOY_VIGENTE
    )

    assert descuento == Decimal("1799.93")


def test_cupon_vencido_el_dia_siguiente():
    assert codigo_de_error(
        calcular_descuento,
        Decimal("30000.00"),
        1,
        "EGRESADOS2026",
        date(2026, 12, 1),
    ) == "CUPON_VENCIDO"

def test_cupon_fijo_acepta_subtotal_minimo():
    descuento = calcular_descuento(
        Decimal("20000.00"),
        1,
        "BIENVENIDA",
        HOY_VIGENTE,
    )

    assert descuento == Decimal("3000.00")

def test_cupon_vigente_en_fecha_limite():
    descuento = calcular_descuento(
        Decimal("20000.00"),
        1,
        "EGRESADOS2026",
        date(2026, 11, 30),
    )

    assert descuento == Decimal("3000.00")


def test_cupon_vacio_equivale_a_sin_cupon():
    descuento = calcular_descuento(
        Decimal("10000.00"), 1, "   ", HOY_VIGENTE
    )

    assert descuento == Decimal("0.00")


def test_descuento_por_cantidad_no_se_suma_al_cupon():
    descuento = calcular_descuento(
        Decimal("100000.00"), 5, "EGRESADOS2026", HOY_VIGENTE
    )

    assert descuento == Decimal("15000.00")


def test_descuento_fijo_requiere_minimo():
    assert codigo_de_error(
        calcular_descuento,
        Decimal("19999.99"),
        1,
        "BIENVENIDA",
        HOY_VIGENTE,
    ) == "CUPON_MINIMO_NO_ALCANZADO"


def test_cupon_inventado_es_invalido():
    assert codigo_de_error(
        calcular_descuento,
        Decimal("30000.00"),
        1,
        "DEBUG100",
        HOY_VIGENTE,
    ) == "CUPON_INVALIDO"


def test_envio_gratis_desde_sesenta_mil():
    assert calcular_envio(Decimal("60000.00"), "CABA") == Decimal("0.00")


def test_zona_normaliza_mayusculas_y_espacios():
    assert calcular_envio(Decimal("10000.00"), " caba ") == Decimal("2500.00")


def test_zona_inexistente_lanza_error():
    assert codigo_de_error(
        calcular_envio, Decimal("10000.00"), "PATAGONIA"
    ) == "ZONA_INVALIDA"


def test_carrito_vacio_lanza_error():
    assert codigo_de_error(calcular_total, [], "CABA") == "CARRITO_VACIO"


def test_total_respeta_la_formula():
    resultado = calcular_total(
        [item(cantidad=2)], "CABA", fecha=HOY_VIGENTE
    )

    assert resultado == {
        "subtotal": Decimal("49999.80"),
        "descuento": Decimal("0.00"),
        "envio": Decimal("2500.00"),
        "total": Decimal("52499.80"),
    }
