"""Pruebas adicionales del equipo (no sustituyen ni modifican test_security.py)."""
import pytest
from decimal import Decimal
from .conftest import authenticate
from src.validators import validar_calificacion


@pytest.mark.parametrize('ok', [85, 99.5, '99.50', '0', '100', 100.0])
def test_validador_acepta(ok):
    assert Decimal('0') <= validar_calificacion(ok) <= Decimal('100')


@pytest.mark.parametrize('bad', [True, False, float('nan'), float('inf'), '1e1', '1_0', ' 85', '+5', '100.01', 99.999, [], {}])
def test_validador_rechaza(bad):
    with pytest.raises(ValueError):
        validar_calificacion(bad)


def test_sin_sesion_401(client):
    assert client.get('/grades/3/10').status_code == 401
    assert client.put('/grades/3/10', json={'grade': '90'}).status_code == 401


def test_admin_no_modifica_por_defecto(client):
    headers = authenticate(client, 'admin_demo')
    assert client.put('/grades/3/10', json={'grade': '90'}, headers=headers).status_code == 403


def test_estudiante_propio_get_200(client):
    authenticate(client, 'alumna_eli')
    assert client.get('/grades/3/10').status_code == 200


def test_profesor_ajeno_no_lee(client):
    authenticate(client, 'profe_luis')
    assert client.get('/grades/3/10').status_code == 403


def test_estudiante_no_inscrito_denegado(client):
    # alumna_eli (3) no está inscrita en el grupo 20, aunque pida su propio id.
    authenticate(client, 'alumna_eli')
    assert client.get('/grades/3/20').status_code == 403


def test_profesor_propio_grupo_estudiante_no_inscrito(client):
    # profe_ana (grupo 10) no puede crear nota de un alumno no inscrito en 10.
    headers = authenticate(client, 'profe_ana')
    assert client.put('/grades/4/10', json={'grade': '80'}, headers=headers).status_code == 403


def test_sin_outbox_si_se_deniega(client):
    from src.db import connect
    headers = authenticate(client, 'profe_ana')
    client.put('/grades/4/20', json={'grade': '80'}, headers=headers)
    with connect(client.application.config['DB_PATH']) as con:
        assert con.execute('SELECT COUNT(*) FROM notification_outbox').fetchone()[0] == 0


def test_error_no_expone_traza(client):
    headers = authenticate(client, 'profe_ana')
    res = client.put('/grades/3/10', json={'grade': 'hola'}, headers=headers)
    assert res.status_code == 400 and 'Traceback' not in res.get_data(as_text=True)
