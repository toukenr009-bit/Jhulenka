path = "app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insertar el modelo Favorito justo antes del comentario de decoradores
anchor1 = "# ==================== DECORADORES"
assert content.count(anchor1) == 1, f"ANCHOR 1: se encontraron {content.count(anchor1)} coincidencias"

clase_favorito = """class Favorito(db.Model):
    __tablename__ = 'favoritos'

    id_favorito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_libro = db.Column(db.Integer, db.ForeignKey('libros.id_libro'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='FAVORITO')
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)

    libro_rel = db.relationship('Libro')

    def to_dict(self):
        return {
            'id_favorito': self.id_favorito,
            'id_usuario': self.id_usuario,
            'id_libro': self.id_libro,
            'tipo': self.tipo,
            'fecha_agregado': self.fecha_agregado.isoformat() if self.fecha_agregado else None,
            'libro': self.libro_rel.to_dict() if self.libro_rel else None
        }

"""
content = content.replace(anchor1, clase_favorito + anchor1, 1)

# 2. Insertar las rutas nuevas justo antes de la ruta principal
anchor2 = "# ==================== RUTA PRINCIPAL"
assert content.count(anchor2) == 1, f"ANCHOR 2: se encontraron {content.count(anchor2)} coincidencias"

rutas_favoritos = """# ==================== RUTAS DE FAVORITOS / LEIDOS ====================
@app.route('/api/favoritos', methods=['GET'])
@token_required
def obtener_favoritos(current_user):
    tipo = request.args.get('tipo')
    query = Favorito.query.filter_by(id_usuario=current_user.id_usuario)
    if tipo:
        query = query.filter_by(tipo=tipo)
    favoritos = query.all()
    return jsonify({'favoritos': [f.to_dict() for f in favoritos]}), 200

@app.route('/api/favoritos', methods=['POST'])
@token_required
def agregar_favorito(current_user):
    data = request.get_json()
    if not data or 'id_libro' not in data:
        return jsonify({'error': 'id_libro es obligatorio'}), 400

    tipo = data.get('tipo', 'FAVORITO')
    if tipo not in ['FAVORITO', 'LEIDO']:
        return jsonify({'error': 'tipo invalido'}), 400

    libro = Libro.query.get(data['id_libro'])
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404

    existente = Favorito.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_libro=data['id_libro'],
        tipo=tipo
    ).first()
    if existente:
        return jsonify({'mensaje': 'Ya estaba agregado', 'favorito': existente.to_dict()}), 200

    nuevo = Favorito(
        id_usuario=current_user.id_usuario,
        id_libro=data['id_libro'],
        tipo=tipo
    )
    try:
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({'mensaje': 'Agregado exitosamente', 'favorito': nuevo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al agregar: {str(e)}'}), 500

@app.route('/api/favoritos/<int:id_libro>', methods=['DELETE'])
@token_required
def quitar_favorito(current_user, id_libro):
    tipo = request.args.get('tipo', 'FAVORITO')
    favorito = Favorito.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_libro=id_libro,
        tipo=tipo
    ).first()
    if not favorito:
        return jsonify({'error': 'No encontrado'}), 404
    try:
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({'mensaje': 'Eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar: {str(e)}'}), 500

"""
content = content.replace(anchor2, rutas_favoritos + anchor2, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, backend de favoritos/leidos creado.")
