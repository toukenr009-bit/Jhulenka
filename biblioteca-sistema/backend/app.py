"""
Sistema Inteligente de Gestión de Biblioteca
Backend - Flask API
Sprint 1: Usuarios, Catálogo, Préstamos, Devoluciones y Reservas
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import jwt
import bcrypt
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Configuración de la base de datos MySQL (XAMPP)
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'biblioteca')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_charset = os.getenv('DB_CHARSET', 'utf8mb4')

# Construir URI de conexión a MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset={db_charset}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-cambia-esto')

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# ==================== MODELOS DE BASE DE DATOS ====================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    carnet = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    tipo_usuario = db.Column(db.String(30), nullable=False)
    estado = db.Column(db.String(20), default='ACTIVO')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con préstamos
    prestamos = db.relationship(
        'Prestamo',
        foreign_keys='Prestamo.id_usuario',
        backref='usuario',
        lazy=True
    )
    prestamos_creados = db.relationship(
        'Prestamo',
        foreign_keys='Prestamo.creado_por',
        backref='creador',
        lazy=True
    )
    reservas = db.relationship('Reserva', backref='usuario', lazy=True)
    
    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'carnet': self.carnet,
            'correo': self.correo,
            'tipo_usuario': self.tipo_usuario,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='ACTIVA')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con libros
    libros = db.relationship('Libro', backref='categoria', lazy=True)
    
    def to_dict(self):
        return {
            'id_categoria': self.id_categoria,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'estado': self.estado
        }

class Libro(db.Model):
    __tablename__ = 'libros'
    
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(150), nullable=False)
    editorial = db.Column(db.String(100))
    isbn = db.Column(db.String(20), unique=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    anio_publicacion = db.Column(db.Integer)
    ejemplares_totales = db.Column(db.Integer, default=1)
    ejemplares_disponibles = db.Column(db.Integer, default=1)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='ACTIVO')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    prestamos = db.relationship('Prestamo', backref='libro', lazy=True)
    reservas = db.relationship('Reserva', backref='libro', lazy=True)
    
    def to_dict(self):
        return {
            'id_libro': self.id_libro,
            'titulo': self.titulo,
            'autor': self.autor,
            'editorial': self.editorial,
            'isbn': self.isbn,
            'categoria': self.categoria.nombre if self.categoria else None,
            'anio_publicacion': self.anio_publicacion,
            'ejemplares_totales': self.ejemplares_totales,
            'ejemplares_disponibles': self.ejemplares_disponibles,
            'descripcion': self.descripcion,
            'estado': self.estado
        }

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    
    id_prestamo = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_libro = db.Column(db.Integer, db.ForeignKey('libros.id_libro'), nullable=False)
    fecha_prestamo = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.Date, nullable=False)
    fecha_devolucion = db.Column(db.Date)
    estado = db.Column(db.String(30), default='PRESTADO')
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    ci_prenda = db.Column(db.String(20))
    ru_prenda = db.Column(db.String(20))
    celular = db.Column(db.String(20))
    
    # Relación con devoluciones
    devolucion = db.relationship('Devolucion', backref='prestamo', uselist=False)
    
    def to_dict(self):
        return {
            'id_prestamo': self.id_prestamo,
            'id_usuario': self.id_usuario,
            'id_libro': self.id_libro,
            'usuario': self.usuario.nombre + ' ' + self.usuario.apellido if self.usuario else None,
            'libro': self.libro.titulo if self.libro else None,
            'fecha_prestamo': self.fecha_prestamo.isoformat() if self.fecha_prestamo else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'fecha_devolucion': self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            'estado': self.estado,
            'ci_prenda': self.ci_prenda,
            'ru_prenda': self.ru_prenda,
            'celular': self.celular
        }

class Devolucion(db.Model):
    __tablename__ = 'devoluciones'
    
    id_devolucion = db.Column(db.Integer, primary_key=True)
    id_prestamo = db.Column(db.Integer, db.ForeignKey('prestamos.id_prestamo'), nullable=False)
    fecha_devolucion = db.Column(db.DateTime, default=datetime.utcnow)
    dias_retraso = db.Column(db.Integer, default=0)
    multa_generada = db.Column(db.Float, default=0.0)
    estado_multa = db.Column(db.String(20), default='PENDIENTE')
    
    def to_dict(self):
        return {
            'id_devolucion': self.id_devolucion,
            'id_prestamo': self.id_prestamo,
            'fecha_devolucion': self.fecha_devolucion.isoformat() if self.fecha_devolucion else None,
            'dias_retraso': self.dias_retraso,
            'multa_generada': self.multa_generada,
            'estado_multa': self.estado_multa,
            'usuario': self.prestamo.usuario.nombre + ' ' + self.prestamo.usuario.apellido if (self.prestamo and self.prestamo.usuario) else 'Desconocido'
        }

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_libro = db.Column(db.Integer, db.ForeignKey('libros.id_libro'), nullable=False)
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(30), default='ACTIVA')
    posicion_lista = db.Column(db.Integer, default=1)
    
    def to_dict(self):
        return {
            'id_reserva': self.id_reserva,
            'usuario': self.usuario.nombre + ' ' + self.usuario.apellido if self.usuario else None,
            'libro': self.libro.titulo if self.libro else None,
            'fecha_reserva': self.fecha_reserva.isoformat() if self.fecha_reserva else None,
            'estado': self.estado,
            'posicion_lista': self.posicion_lista
        }

# ==================== DECORADORES DE AUTENTICACIÓN ====================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['id_usuario'])
            if not current_user:
                return jsonify({'error': 'Usuario no encontrado'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get('Authorization'):
            token = request.headers['Authorization'].split(' ')[1]
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user = Usuario.query.get(data['id_usuario'])
                if not user or user.tipo_usuario != 'ADMINISTRADOR':
                    return jsonify({'error': 'Se requiere rol de administrador'}), 403
            except:
                return jsonify({'error': 'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorated

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/usuarios/registro', methods=['POST'])
def registrar_usuario():
    """
    IN-A01: Registro y validación de usuarios
    Crear formulario de registro con validación de nombre, correo, carnet y tipo de usuario.
    Implementar estado activo/inactivo. Configurar permisos básicos por rol.
    """
    data = request.get_json()
    
    # Validaciones
    if not data or not all(k in data for k in ['nombre', 'apellido', 'carnet', 'correo', 'tipo_usuario']):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    
    # Validar tipo de usuario
    if data['tipo_usuario'] not in ['ADMINISTRADOR', 'LECTOR']:
        return jsonify({'error': 'Tipo de usuario inválido'}), 400
    
    # Verificar si el carnet ya existe
    if Usuario.query.filter_by(carnet=data['carnet']).first():
        return jsonify({'error': 'El carnet ya está registrado'}), 409
    
    # Verificar si el correo ya existe
    if Usuario.query.filter_by(correo=data['correo']).first():
        return jsonify({'error': 'El correo ya está registrado'}), 409
    
    # Validar formato de correo
    import re
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['correo']):
        return jsonify({'error': 'Formato de correo inválido'}), 400
    
    # Crear usuario
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        apellido=data['apellido'],
        carnet=data['carnet'],
        correo=data['correo'],
        tipo_usuario=data['tipo_usuario'],
        estado='ACTIVO'
    )
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({'mensaje': 'Usuario registrado exitosamente', 'usuario': nuevo_usuario.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar usuario: {str(e)}'}), 500

@app.route('/api/usuarios/login', methods=['POST'])
def login():
    """
    Autenticación de usuarios
    """
    data = request.get_json()
    
    if not data or 'correo' not in data or 'carnet' not in data:
        return jsonify({'error': 'Correo y carnet son requeridos'}), 400
    
    # Buscar usuario por correo y carnet
    usuario = Usuario.query.filter_by(correo=data['correo'], carnet=data['carnet']).first()
    
    if not usuario:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    if usuario.estado != 'ACTIVO':
        return jsonify({'error': 'Usuario inactivo. Contacte al administrador.'}), 403
    
    # Generar token JWT
    token = jwt.encode({
        'id_usuario': usuario.id_usuario,
        'tipo_usuario': usuario.tipo_usuario,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'mensaje': 'Login exitoso',
        'token': token,
        'usuario': usuario.to_dict()
    }), 200

# ==================== RUTAS DE USUARIOS ====================

@app.route('/api/usuarios', methods=['GET'])
@token_required
def obtener_usuarios(current_user):
    """
    Obtener lista de usuarios (solo administradores)
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    usuarios = Usuario.query.filter_by(estado='ACTIVO').all()
    return jsonify({'usuarios': [u.to_dict() for u in usuarios]}), 200

@app.route('/api/usuarios/<int:id>', methods=['PUT'])
@token_required
def actualizar_usuario(current_user, id):
    """
    Actualizar usuario (solo administradores)
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    # Actualizar campos permitidos
    if 'nombre' in data:
        usuario.nombre = data['nombre']
    if 'apellido' in data:
        usuario.apellido = data['apellido']
    if 'correo' in data:
        usuario.correo = data['correo']
    if 'estado' in data and data['estado'] in ['ACTIVO', 'INACTIVO']:
        usuario.estado = data['estado']
    
    try:
        db.session.commit()
        return jsonify({'mensaje': 'Usuario actualizado', 'usuario': usuario.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar: {str(e)}'}), 500

# ==================== RUTAS DE CATEGORÍAS ====================

@app.route('/api/categorias', methods=['GET'])
def obtener_categorias():
    """
    Obtener lista de categorías
    """
    categorias = Categoria.query.filter_by(estado='ACTIVA').all()
    return jsonify({'categorias': [c.to_dict() for c in categorias]}), 200

@app.route('/api/categorias', methods=['POST'])
@token_required
def crear_categoria(current_user):
    """
    Crear categoría (solo administradores)
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    data = request.get_json()
    
    if not data or 'nombre' not in data:
        return jsonify({'error': 'Nombre de categoría requerido'}), 400
    
    # Verificar si ya existe
    if Categoria.query.filter_by(nombre=data['nombre']).first():
        return jsonify({'error': 'La categoría ya existe'}), 409
    
    nueva_categoria = Categoria(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', '')
    )
    
    try:
        db.session.add(nueva_categoria)
        db.session.commit()
        return jsonify({'mensaje': 'Categoría creada', 'categoria': nueva_categoria.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear categoría: {str(e)}'}), 500

# ==================== RUTAS DE LIBROS (IN-A02) ====================

@app.route('/api/libros', methods=['GET'])
def obtener_libros():
    """
    IN-A02: Gestión de catálogo inicial
    Consultar libros con filtros opcionales
    """
    # Obtener parámetros de filtro
    titulo = request.args.get('titulo')
    autor = request.args.get('autor')
    isbn = request.args.get('isbn')
    categoria = request.args.get('categoria')
    disponible = request.args.get('disponible')
    
    # Construir consulta
    query = Libro.query.filter_by(estado='ACTIVO')
    
    if titulo:
        query = query.filter(Libro.titulo.ilike(f'%{titulo}%'))
    if autor:
        query = query.filter(Libro.autor.ilike(f'%{autor}%'))
    if isbn:
        query = query.filter(Libro.isbn == isbn)
    if categoria:
        query = query.join(Categoria).filter(Categoria.nombre == categoria)
    if disponible:
        query = query.filter(Libro.ejemplares_disponibles > 0)
    
    libros = query.all()
    return jsonify({'libros': [l.to_dict() for l in libros]}), 200

@app.route('/api/libros/<int:id>', methods=['GET'])
def obtener_libro(id):
    """
    Obtener detalle de un libro específico
    """
    libro = Libro.query.get(id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    return jsonify({'libro': libro.to_dict()}), 200

@app.route('/api/libros', methods=['POST'])
@token_required
def crear_libro(current_user):
    """
    IN-A02: Gestión de catálogo inicial
    Crear módulo para registrar libros con título, autor, editorial, ISBN, categoría, año y ejemplares disponibles.
    Validar campos obligatorios y duplicados.
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    data = request.get_json()
    
    # Validar campos obligatorios
    campos_obligatorios = ['titulo', 'autor', 'isbn']
    if not data or not all(k in data for k in campos_obligatorios):
        return jsonify({'error': f'Campos obligatorios: {", ".join(campos_obligatorios)}'}), 400
    
    # Verificar ISBN duplicado
    if Libro.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': 'El ISBN ya está registrado'}), 409
    
    # Verificar categoría si se proporciona
    id_categoria = None
    if 'id_categoria' in data:
        categoria = Categoria.query.get(data['id_categoria'])
        if not categoria:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        id_categoria = data['id_categoria']
    
    # Establecer valores por defecto
    ejemplares_totales = data.get('ejemplares_totales', 1)
    ejemplares_disponibles = data.get('ejemplares_disponibles', ejemplares_totales)
    
    nuevo_libro = Libro(
        titulo=data['titulo'],
        autor=data['autor'],
        editorial=data.get('editorial'),
        isbn=data['isbn'],
        id_categoria=id_categoria,
        anio_publicacion=data.get('anio_publicacion'),
        ejemplares_totales=ejemplares_totales,
        ejemplares_disponibles=ejemplares_disponibles,
        descripcion=data.get('descripcion'),
        estado='ACTIVO'
    )
    
    try:
        db.session.add(nuevo_libro)
        db.session.commit()
        return jsonify({'mensaje': 'Libro registrado exitosamente', 'libro': nuevo_libro.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar libro: {str(e)}'}), 500

@app.route('/api/libros/<int:id>', methods=['PUT'])
@token_required
def actualizar_libro(current_user, id):
    """
    Actualizar libro (solo administradores)
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    libro = Libro.query.get(id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    data = request.get_json()
    
    # Actualizar campos permitidos
    campos_permitidos = ['titulo', 'autor', 'editorial', 'id_categoria', 'anio_publicacion', 'descripcion']
    for campo in campos_permitidos:
        if campo in data:
            setattr(libro, campo, data[campo])
    
    # Actualizar ejemplares si se proporciona
    if 'ejemplares_totales' in data:
        libro.ejemplares_totales = data['ejemplares_totales']
    
    try:
        db.session.commit()
        return jsonify({'mensaje': 'Libro actualizado', 'libro': libro.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar: {str(e)}'}), 500

# ==================== RUTAS DE PRÉSTAMOS (IN-U02) ====================

@app.route('/api/prestamos', methods=['GET'])
@token_required
def obtener_prestamos(current_user):
    """
    Obtener lista de préstamos
    """
    # Filtrar por estado si se proporciona
    estado = request.args.get('estado')
    query = Prestamo.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    # Si no es administrador, solo ver sus propios préstamos
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        query = query.filter_by(id_usuario=current_user.id_usuario)
    
    prestamos = query.all()
    return jsonify({'prestamos': [p.to_dict() for p in prestamos]}), 200

@app.route('/api/prestamos', methods=['POST'])
@token_required
def crear_prestamo(current_user):
    """
    IN-U02: Préstamo de ejemplares
    Registrar préstamo con fecha automática, fecha de vencimiento y usuario responsable.
    Descontar stock disponible y bloquear si no hay ejemplares.
    """
    data = request.get_json()
    
    if not data or 'id_usuario' not in data or 'id_libro' not in data:
        return jsonify({'error': 'ID de usuario y libro requeridos'}), 400
        
    # Si no es administrador, verificar que solo pueda solicitar para sí mismo
    if current_user.tipo_usuario != 'ADMINISTRADOR' and int(data['id_usuario']) != current_user.id_usuario:
        return jsonify({'error': 'No tienes permiso para registrar préstamo a otro usuario'}), 403
    
    # Verificar usuario
    usuario = Usuario.query.get(data['id_usuario'])
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    if usuario.estado != 'ACTIVO':
        return jsonify({'error': 'Usuario inactivo. No puede realizar préstamos.'}), 403
    
    # Verificar libro
    libro = Libro.query.get(data['id_libro'])
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    if libro.estado != 'ACTIVO':
        return jsonify({'error': 'Libro inactivo'}), 403
    
    # Verificar disponibilidad
    if libro.ejemplares_disponibles <= 0:
        return jsonify({'error': 'No hay ejemplares disponibles para préstamo'}), 409
    
    # Calcular fecha de vencimiento (14 días por defecto)
    dias_prestamo = data.get('dias_prestamo', 14)
    fecha_vencimiento = datetime.utcnow() + timedelta(days=dias_prestamo)
    
    nuevo_prestamo = Prestamo(
        id_usuario=data['id_usuario'],
        id_libro=data['id_libro'],
        fecha_vencimiento=fecha_vencimiento.date(),
        estado='PRESTADO',
        creado_por=current_user.id_usuario,
        ci_prenda=data.get('ci_prenda'),
        ru_prenda=data.get('ru_prenda'),
        celular=data.get('celular')
    )
    
    try:
        db.session.add(nuevo_prestamo)
        # Descontar ejemplar disponible
        libro.ejemplares_disponibles -= 1
        db.session.commit()
        return jsonify({'mensaje': 'Préstamo registrado exitosamente', 'prestamo': nuevo_prestamo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar préstamo: {str(e)}'}), 500

@app.route('/api/prestamos/<int:id>', methods=['PUT'])
@token_required
def actualizar_prestamo(current_user, id):
    """
    Actualizar préstamo (solo administradores)
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    prestamo = Prestamo.query.get(id)
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    data = request.get_json()
    
    # Solo permitir actualizar estado si es devolución
    if 'estado' in data and data['estado'] == 'DEVUELTO':
        prestamo.estado = 'DEVUELTO'
        prestamo.fecha_devolucion = datetime.utcnow().date()
    
    try:
        db.session.commit()
        return jsonify({'mensaje': 'Préstamo actualizado', 'prestamo': prestamo.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar: {str(e)}'}), 500

# ==================== RUTAS DE DEVOLUCIONES (IN-U03) ====================

@app.route('/api/devoluciones', methods=['GET'])
@token_required
def obtener_devoluciones(current_user):
    """
    Obtener lista de devoluciones
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        devoluciones = Devolucion.query.join(Prestamo).filter(Prestamo.id_usuario == current_user.id_usuario).all()
    else:
        devoluciones = Devolucion.query.all()
    return jsonify({'devoluciones': [d.to_dict() for d in devoluciones]}), 200

@app.route('/api/devoluciones', methods=['POST'])
@token_required
def registrar_devolucion(current_user):
    """
    IN-U03: Devolución y cálculo de retraso
    Registrar devolución, actualizar inventario y calcular días de atraso.
    Marcar estado como devuelto o con multa pendiente.
    """
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'Se requiere rol de administrador'}), 403
    
    data = request.get_json()
    
    if not data or 'id_prestamo' not in data:
        return jsonify({'error': 'ID de préstamo requerido'}), 400
    
    # Buscar préstamo
    prestamo = Prestamo.query.get(data['id_prestamo'])
    if not prestamo:
        return jsonify({'error': 'Préstamo no encontrado'}), 404
    
    if prestamo.estado != 'PRESTADO':
        return jsonify({'error': 'El préstamo ya fue devuelto o no está activo'}), 409
    
    # Calcular días de retraso
    fecha_hoy = datetime.utcnow().date()
    dias_retraso = max(0, (fecha_hoy - prestamo.fecha_vencimiento).days)
    
    # Calcular multa (1.00 por día de retraso)
    multa_generada = dias_retraso * 1.00
    
    # Actualizar préstamo
    prestamo.estado = 'DEVUELTO'
    prestamo.fecha_devolucion = fecha_hoy
    
    # Actualizar disponibilidad del libro
    libro = Libro.query.get(prestamo.id_libro)
    if libro:
        libro.ejemplares_disponibles += 1
    
    # Crear registro de devolución
    nueva_devolucion = Devolucion(
        id_prestamo=data['id_prestamo'],
        dias_retraso=dias_retraso,
        multa_generada=multa_generada,
        estado_multa='PENDIENTE' if multa_generada > 0 else 'PAGADA'
    )
    
    try:
        db.session.add(nueva_devolucion)
        db.session.commit()
        return jsonify({
            'mensaje': 'Devolución registrada exitosamente',
            'devolucion': nueva_devolucion.to_dict(),
            'prestamo': prestamo.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar devolución: {str(e)}'}), 500

# ==================== RUTAS DE RESERVAS (IN-U05) ====================

@app.route('/api/reservas', methods=['GET'])
@token_required
def obtener_reservas(current_user):
    """
    Obtener lista de reservas
    """
    # Si no es administrador, solo ver sus propias reservas
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        reservas = Reserva.query.filter_by(id_usuario=current_user.id_usuario, estado='ACTIVA').all()
    else:
        reservas = Reserva.query.filter_by(estado='ACTIVA').all()
    
    return jsonify({'reservas': [r.to_dict() for r in reservas]}), 200

@app.route('/api/reservas', methods=['POST'])
@token_required
def crear_reserva(current_user):
    """
    IN-U05: Reservas de libros
    Permitir reservar ejemplares disponibles. Registrar turno de espera y cambio automático de estado.
    Notificar al usuario cuando el libro esté libre.
    """
    data = request.get_json()
    
    if not data or 'id_libro' not in data:
        return jsonify({'error': 'ID de libro requerido'}), 400
    
    # Verificar libro
    libro = Libro.query.get(data['id_libro'])
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404
    
    if libro.estado != 'ACTIVO':
        return jsonify({'error': 'Libro inactivo'}), 403
    
    # Verificar si el usuario ya tiene una reserva activa para este libro
    reserva_existente = Reserva.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_libro=data['id_libro'],
        estado='ACTIVA'
    ).first()
    
    if reserva_existente:
        return jsonify({'error': 'Ya tienes una reserva activa para este libro'}), 409
    
    # Calcular posición en lista de espera
    reservas_activas = Reserva.query.filter_by(id_libro=data['id_libro'], estado='ACTIVA').count()
    posicion_lista = reservas_activas + 1
    
    nueva_reserva = Reserva(
        id_usuario=current_user.id_usuario,
        id_libro=data['id_libro'],
        estado='ACTIVA',
        posicion_lista=posicion_lista
    )
    
    try:
        db.session.add(nueva_reserva)
        db.session.commit()
        return jsonify({
            'mensaje': 'Reserva creada exitosamente',
            'reserva': nueva_reserva.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear reserva: {str(e)}'}), 500

@app.route('/api/reservas/<int:id>', methods=['DELETE'])
@token_required
def cancelar_reserva(current_user, id):
    """
    Cancelar reserva
    """
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    
    # Solo el dueño de la reserva o un administrador puede cancelarla
    if reserva.id_usuario != current_user.id_usuario and current_user.tipo_usuario != 'ADMINISTRADOR':
        return jsonify({'error': 'No tienes permiso para cancelar esta reserva'}), 403
    
    reserva.estado = 'CANCELADA'
    
    # Actualizar posiciones de lista de espera
    reservas = Reserva.query.filter_by(id_libro=reserva.id_libro, estado='ACTIVA').order_by(Reserva.posicion_lista).all()
    for i, r in enumerate(reservas, 1):
        r.posicion_lista = i
    
    try:
        db.session.commit()
        return jsonify({'mensaje': 'Reserva cancelada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cancelar reserva: {str(e)}'}), 500

# ==================== RUTAS DE ESTADÍSTICAS ====================

@app.route('/api/estadisticas', methods=['GET'])
@token_required
def obtener_estadisticas(current_user):
    """
    Obtener estadísticas del sistema
    """
    total_libros = Libro.query.filter_by(estado='ACTIVO').count()
    
    if current_user.tipo_usuario != 'ADMINISTRADOR':
        prestamos_activos = Prestamo.query.filter_by(id_usuario=current_user.id_usuario, estado='PRESTADO').count()
        reservas_activas = Reserva.query.filter_by(id_usuario=current_user.id_usuario, estado='ACTIVA').count()
        
        return jsonify({
            'total_usuarios': 0,
            'total_libros': total_libros,
            'prestamos_activos': prestamos_activos,
            'reservas_activas': reservas_activas,
            'libros_mas_prestados': []
        }), 200

    # Contar registros
    total_usuarios = Usuario.query.filter_by(estado='ACTIVO').count()
    prestamos_activos = Prestamo.query.filter_by(estado='PRESTADO').count()
    reservas_activas = Reserva.query.filter_by(estado='ACTIVA').count()
    
    # Libros más prestados
    from sqlalchemy import func
    libros_mas_prestados = db.session.query(
        Libro.titulo, 
        func.count(Prestamo.id_prestamo).label('total_prestamos')
    ).join(Prestamo).group_by(Libro.id_libro).order_by(func.count(Prestamo.id_prestamo).desc()).limit(5).all()
    
    return jsonify({
        'total_usuarios': total_usuarios,
        'total_libros': total_libros,
        'prestamos_activos': prestamos_activos,
        'reservas_activas': reservas_activas,
        'libros_mas_prestados': [
            {'titulo': l.titulo, 'total_prestamos': l.total_prestamos} 
            for l in libros_mas_prestados
        ]
    }), 200

# ==================== INICIALIZAR BASE DE DATOS ====================

def inicializar_base_datos():
    """
    Inicializar la base de datos con datos de ejemplo
    """
    with app.app_context():
        db.create_all()
        
        # Verificar y agregar columnas de prenda si no existen
        try:
            db.session.execute(db.text("SELECT ci_prenda, ru_prenda, celular FROM prestamos LIMIT 1"))
        except Exception:
            db.session.rollback()
            for col in ['ci_prenda', 'ru_prenda', 'celular']:
                try:
                    db.session.execute(db.text(f"ALTER TABLE prestamos ADD COLUMN {col} VARCHAR(20)"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()
        
        # Verificar si ya hay categorías
        if Categoria.query.count() == 0:
            categorias_data = [
                {'nombre': 'Ficción', 'descripcion': 'Literatura de ficción general'},
                {'nombre': 'Ciencia Ficción', 'descripcion': 'Novelas de ciencia ficción y fantasía'},
                {'nombre': 'Tecnología', 'descripcion': 'Libros sobre tecnología y programación'},
                {'nombre': 'Educación', 'descripcion': 'Material educativo y académico'},
                {'nombre': 'Historia', 'descripcion': 'Libros de historia y biografías'},
                {'nombre': 'Matemáticas', 'descripcion': 'Textos de matemáticas y lógica'}
            ]
            
            for cat_data in categorias_data:
                categoria = Categoria(**cat_data)
                db.session.add(categoria)
            
            db.session.commit()
        
        # Verificar si ya hay administrador
        if Usuario.query.filter_by(tipo_usuario='ADMINISTRADOR').count() == 0:
            admin = Usuario(
                nombre='Admin',
                apellido='Biblioteca',
                carnet='ADMIN001',
                correo='admin@biblioteca.com',
                tipo_usuario='ADMINISTRADOR',
                estado='ACTIVO'
            )
            db.session.add(admin)
            db.session.commit()
        
        # Verificar si ya hay libros
        if Libro.query.count() == 0:
            libros_data = [
                {
                    'titulo': 'Fundamentos de Programación',
                    'autor': 'Luis Joyanes',
                    'editorial': 'McGraw-Hill',
                    'isbn': '978-9701072450',
                    'id_categoria': 3,
                    'anio_publicacion': 2020,
                    'ejemplares_totales': 5,
                    'ejemplares_disponibles': 5,
                    'descripcion': 'Libro básico de programación'
                },
                {
                    'titulo': 'Matemáticas Discretas',
                    'autor': 'Richard Johnsonbaugh',
                    'editorial': 'Pearson',
                    'isbn': '978-6073220586',
                    'id_categoria': 6,
                    'anio_publicacion': 2019,
                    'ejemplares_totales': 3,
                    'ejemplares_disponibles': 3,
                    'descripcion': 'Matemáticas para ciencias de la computación'
                },
                {
                    'titulo': 'Historia Universal',
                    'autor': 'José Luis Esquivel',
                    'editorial': 'Editorial Patria',
                    'isbn': '978-6075320123',
                    'id_categoria': 5,
                    'anio_publicacion': 2021,
                    'ejemplares_totales': 2,
                    'ejemplares_disponibles': 2,
                    'descripcion': 'Historia general de la humanidad'
                },
                {
                    'titulo': 'Introducción a la Física',
                    'autor': 'Paul Tipler',
                    'editorial': 'Editorial Reverté',
                    'isbn': '978-8429144295',
                    'id_categoria': 4,
                    'anio_publicacion': 2018,
                    'ejemplares_totales': 4,
                    'ejemplares_disponibles': 4,
                    'descripcion': 'Física básica para estudiantes'
                },
                {
                    'titulo': 'El Señor de los Anillos',
                    'autor': 'J.R.R. Tolkien',
                    'editorial': 'Minotauro',
                    'isbn': '978-9877380789',
                    'id_categoria': 2,
                    'anio_publicacion': 2020,
                    'ejemplares_totales': 3,
                    'ejemplares_disponibles': 3,
                    'descripcion': 'Trilogía de fantasía épica'
                }
            ]
            
            for libro_data in libros_data:
                libro = Libro(**libro_data)
                db.session.add(libro)
            
            db.session.commit()

# ==================== RUTA PRINCIPAL ====================

@app.route('/')
def index():
    return jsonify({
        'mensaje': 'Sistema Inteligente de Gestión de Biblioteca',
        'version': '1.0.0',
        'sprint': 'Sprint 1',
        'endpoints': {
            'usuarios': '/api/usuarios',
            'categorias': '/api/categorias',
            'libros': '/api/libros',
            'prestamos': '/api/prestamos',
            'devoluciones': '/api/devoluciones',
            'reservas': '/api/reservas',
            'estadisticas': '/api/estadisticas'
        }
    })

# ==================== INICIALIZAR AL ARRANCAR ====================

# Esto corre tanto con gunicorn como con python app.py
with app.app_context():
    inicializar_base_datos()

# ==================== EJECUTAR APLICACIÓN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)