import re
from decimal import Decimal

# 1 a 3 dígitos enteros y, opcionalmente, 1 o 2 decimales. Sin signo, sin
# notación científica, sin espacios ni guiones bajos (Decimal los aceptaría).
_PATRON = re.compile(r'[0-9]{1,3}(\.[0-9]{1,2})?')
_MIN = Decimal('0')
_MAX = Decimal('100')


def validar_calificacion(valor):
    """Devuelve un Decimal entre 0 y 100 con máximo dos decimales.

    Lanza ValueError ante cualquier entrada inválida (la app responde 400).
    Nunca redondea: 99.999 se rechaza, no se convierte en 100.
    """
    # bool es subclase de int: debe rechazarse antes de cualquier conversión.
    if valor is None or isinstance(valor, bool):
        raise ValueError('Calificación inválida')
    if not isinstance(valor, (int, float, str, Decimal)):
        raise ValueError('Calificación inválida')

    texto = format(valor, 'f') if isinstance(valor, Decimal) else str(valor)
    # NaN e Infinity no cumplen el patrón numérico y se rechazan aquí.
    if not _PATRON.fullmatch(texto):
        raise ValueError('Calificación inválida')

    numero = Decimal(texto)
    if not (_MIN <= numero <= _MAX):
        raise ValueError('Calificación fuera de rango')
    return numero
