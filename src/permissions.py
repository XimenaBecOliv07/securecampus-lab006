# Principio: denegar por defecto. Toda decisión se toma con datos del servidor
# (tablas groups y enrollments), nunca con datos enviados por el cliente.

def _inscrito(con, student_id, group_id):
    return con.execute(
        'SELECT 1 FROM enrollments WHERE student_id=? AND group_id=?',
        (student_id, group_id)).fetchone() is not None


def _profesor_del_grupo(con, user, group_id):
    if user['role'] != 'profesor':
        return False
    return con.execute(
        'SELECT 1 FROM groups WHERE id=? AND professor_id=?',
        (group_id, user['id'])).fetchone() is not None


def puede_modificar(user, student_id, group_id, con):
    # Solo el profesor asignado al grupo Y con el estudiante inscrito en él.
    # Estudiantes y administrador quedan denegados por defecto.
    return _profesor_del_grupo(con, user, group_id) and _inscrito(con, student_id, group_id)


def puede_consultar(user, student_id, group_id, con):
    # Sin inscripción no hay recurso que consultar, para ningún rol.
    if not _inscrito(con, student_id, group_id):
        return False
    if user['role'] == 'estudiante':
        return user['id'] == student_id
    return _profesor_del_grupo(con, user, group_id)
