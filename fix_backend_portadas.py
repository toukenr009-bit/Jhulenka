path = "app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Agregar columna al modelo Libro
old1 = """    estado = db.Column(db.String(20), default='ACTIVO')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    prestamos = db.relationship('Prestamo', backref='libro', lazy=True)"""
new1 = """    estado = db.Column(db.String(20), default='ACTIVO')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    portada_url = db.Column(db.String(500))
    
    # Relaciones
    prestamos = db.relationship('Prestamo', backref='libro', lazy=True)"""
assert old1 in content, "ANCHOR 1 NO ENCONTRADO"
content = content.replace(old1, new1)

# 2. Agregar al to_dict()
old2 = """            'descripcion': self.descripcion,
            'estado': self.estado
        }

class Prestamo(db.Model):"""
new2 = """            'descripcion': self.descripcion,
            'estado': self.estado,
            'portada_url': self.portada_url
        }

class Prestamo(db.Model):"""
assert old2 in content, "ANCHOR 2 NO ENCONTRADO"
content = content.replace(old2, new2)

# 3. Permitir guardar portada_url al crear libro
old3 = """        descripcion=data.get('descripcion'),
        estado='ACTIVO'
    )"""
new3 = """        descripcion=data.get('descripcion'),
        estado='ACTIVO',
        portada_url=data.get('portada_url')
    )"""
assert old3 in content, "ANCHOR 3 NO ENCONTRADO"
content = content.replace(old3, new3)

# 4. Permitir actualizar portada_url
old4 = """    campos_permitidos = ['titulo', 'autor', 'editorial', 'id_categoria', 'anio_publicacion', 'descripcion']"""
new4 = """    campos_permitidos = ['titulo', 'autor', 'editorial', 'id_categoria', 'anio_publicacion', 'descripcion', 'portada_url']"""
assert old4 in content, "ANCHOR 4 NO ENCONTRADO"
content = content.replace(old4, new4)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, backend de portadas actualizado.")
