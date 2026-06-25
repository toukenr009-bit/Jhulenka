/**
 * Sistema Inteligente de Gestión de Biblioteca
 * Frontend JavaScript
 * Sprint 1: Usuarios, Catálogo, Préstamos, Devoluciones y Reservas
 */

// Configuración
const API_BASE_URL = '/api';
const TOKEN_KEY = 'biblioteca_token';

// Estado de la aplicación
const state = {
    currentUser: null,
    currentSection: 'inicio',
    libros: [],
    categorias: [],
    usuarios: [],
    prestamos: [],
    devoluciones: [],
    reservas: []
};

// Elementos del DOM
const elements = {
    // Secciones
    loginSection: document.getElementById('loginSection'),
    registerSection: document.getElementById('registerSection'),
    inicioSection: document.getElementById('inicioSection'),
    librosSection: document.getElementById('librosSection'),
    prestamosSection: document.getElementById('prestamosSection'),
    devolucionesSection: document.getElementById('devolucionesSection'),
    reservasSection: document.getElementById('reservasSection'),
    usuariosSection: document.getElementById('usuariosSection'),

    // Header
    mainNav: document.getElementById('mainNav'),
    userInfo: document.getElementById('userInfo'),
    userName: document.getElementById('userName'),
    userRole: document.getElementById('userRole'),
    logoutBtn: document.getElementById('logoutBtn'),

    // Formularios
    loginForm: document.getElementById('loginForm'),
    registerForm: document.getElementById('registerForm'),

    // Dashboard
    totalLibros: document.getElementById('totalLibros'),
    totalUsuarios: document.getElementById('totalUsuarios'),
    prestamosActivos: document.getElementById('prestamosActivos'),
    reservasActivas: document.getElementById('reservasActivas'),
    librosMasPrestados: document.getElementById('librosMasPrestados'),
    adminSection: document.getElementById('adminSection'),

    // Libros
    librosList: document.getElementById('librosList'),
    booksEmptyState: document.getElementById('booksEmptyState'),
    searchTitulo: document.getElementById('searchTitulo'),
    searchAutor: document.getElementById('searchAutor'),
    searchCategoria: document.getElementById('searchCategoria'),
    searchDisponible: document.getElementById('searchDisponible'),
    addBookBtn: document.getElementById('addBookBtn'),
    refreshBooks: document.getElementById('refreshBooks'),

    // Préstamos
    prestamosList: document.getElementById('prestamosList'),
    filterPrestamoEstado: document.getElementById('filterPrestamoEstado'),
    addLoanBtn: document.getElementById('addLoanBtn'),
    refreshLoans: document.getElementById('refreshLoans'),

    // Devoluciones
    devolucionesList: document.getElementById('devolucionesList'),
    refreshReturns: document.getElementById('refreshReturns'),

    // Reservas
    reservasList: document.getElementById('reservasList'),
    refreshReservations: document.getElementById('refreshReservations'),

    // Usuarios
    usuariosList: document.getElementById('usuariosList'),
    addUserBtn: document.getElementById('addUserBtn'),
    refreshUsers: document.getElementById('refreshUsers'),

    // Modales
    bookModal: document.getElementById('bookModal'),
    loanModal: document.getElementById('loanModal'),
    userModal: document.getElementById('userModal'),
    bookDetailModal: document.getElementById('bookDetailModal'),

    // Toast
    toast: document.getElementById('toast'),
    // Formulario de libro
    bookForm: document.getElementById('bookForm'),
    // Mis Libros / Favoritos
    misLibrosSection: document.getElementById('misLibrosSection'),
    misLibrosLeidos: document.getElementById('misLibrosLeidos'),
    misFavoritosList: document.getElementById('misFavoritosList'),
    misLibrosEmpty: document.getElementById('misLibrosEmpty'),
    refreshMisLibros: document.getElementById('refreshMisLibros'),
    // Reportes
    reportesSection: document.getElementById('reportesSection'),
    reportesList: document.getElementById('reportesList'),
    reportesEmpty: document.getElementById('reportesEmpty'),
    downloadPdfBtn: document.getElementById('downloadPdfBtn'),
    downloadExcelBtn: document.getElementById('downloadExcelBtn'),
    refreshReports: document.getElementById('refreshReports'),
    reportTotalLibros: document.getElementById('reportTotalLibros'),
    reportTotalUsuarios: document.getElementById('reportTotalUsuarios'),
    reportTotalPrestamos: document.getElementById('reportTotalPrestamos'),
    reportTotalDevoluciones: document.getElementById('reportTotalDevoluciones'),
    reportTotalReservas: document.getElementById('reportTotalReservas'),
    reportTotalMultas: document.getElementById('reportTotalMultas')
};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    checkAuth();
    loadCategorias();
});

// Event Listeners
function initEventListeners() {
    // Navegación
    elements.mainNav.addEventListener('click', (e) => {
        if (e.target.closest('.nav-link')) {
            e.preventDefault();
            const section = e.target.closest('.nav-link').dataset.section;
            navigateTo(section);
        }
    });

    // Formularios
    elements.loginForm.addEventListener('submit', handleLogin);
    elements.registerForm.addEventListener('submit', handleRegister);
    elements.logoutBtn.addEventListener('click', handleLogout);

    // Libros
    elements.searchTitulo.addEventListener('input', filterLibros);
    elements.searchAutor.addEventListener('input', filterLibros);
    elements.searchCategoria.addEventListener('change', filterLibros);
    elements.searchDisponible.addEventListener('change', filterLibros);
    elements.addBookBtn.addEventListener('click', () => openBookModal());
    elements.refreshBooks.addEventListener('click', loadLibros);

    // Préstamos
    elements.filterPrestamoEstado.addEventListener('change', filterPrestamos);
    elements.addLoanBtn.addEventListener('click', () => openLoanModal());
    elements.refreshLoans.addEventListener('click', loadPrestamos);

    // Devoluciones
    elements.refreshReturns.addEventListener('click', loadDevoluciones);

    // Reservas
    elements.refreshReservations.addEventListener('click', loadReservas);

    // Usuarios
    elements.addUserBtn.addEventListener('click', () => openUserModal());
    elements.refreshUsers.addEventListener('click', loadUsuarios);

    // Modales
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modalId = e.target.dataset.modal;
            closeModal(modalId);
        });
    });

    // Cerrar modales al hacer clic fuera
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });

    // Formulario de prestarse (Lector)
    const prestarseForm = document.getElementById('prestarseForm');
    if (prestarseForm) {
        prestarseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id_libro = document.getElementById('prestarseLibroId').value;
            const ci = document.getElementById('prestarseCI').value;
            const ru = document.getElementById('prestarseRU').value;
            const celular = document.getElementById('prestarseCelular').value;

            const data = {
                id_usuario: state.currentUser.id_usuario,
                id_libro: id_libro,
                dias_prestamo: 14,
                ci_prenda: ci,
                ru_prenda: ru,
                celular: celular
            };

            try {
                const token = localStorage.getItem(TOKEN_KEY);
                const response = await fetch(`${API_BASE_URL}/prestamos`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    showToast('Préstamo registrado exitosamente', 'success');
                    closeModal('prestarseModal');
                    loadPrestamos();
                    loadDashboard();
                    loadLibros();
                } else {
                    showToast(result.error || 'Error al solicitar préstamo', 'error');
                }
            } catch (error) {
                console.error('Error en solicitar préstamo:', error);
                showToast('Error de conexión', 'error');
            }
        });
    }

    // Mostrar/Ocultar registro
    document.getElementById('showRegister').addEventListener('click', (e) => {
        e.preventDefault();
        toggleSections(elements.loginSection, elements.registerSection);
    });

    document.getElementById('cancelRegister').addEventListener('click', () => {
        toggleSections(elements.registerSection, elements.loginSection);
    });
}

// Autenticación
function checkAuth() {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
        validateToken(token);
    } else {
        showLogin();
    }
}

async function validateToken(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            state.currentUser = JSON.parse(localStorage.getItem('currentUser'));
            showMainApp();
            loadDashboard();
        } else {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem('currentUser');
            showLogin();
        }
    } catch (error) {
        console.error('Error validando token:', error);
        showLogin();
    }
}

async function handleLogin(e) {
    e.preventDefault();

    const correo = document.getElementById('loginCorreo').value;
    const carnet = document.getElementById('loginCarnet').value;

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ correo, carnet })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem(TOKEN_KEY, data.token);
            localStorage.setItem('currentUser', JSON.stringify(data.usuario));
            state.currentUser = data.usuario;
            showMainApp();
            loadDashboard();
            showToast('¡Bienvenido de nuevo!', 'success');
        } else {
            showToast(data.error || 'Error al iniciar sesión', 'error');
        }
    } catch (error) {
        console.error('Error en login:', error);
        showToast('Error de conexión', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();

    const nombre = document.getElementById('registroNombre').value;
    const apellido = document.getElementById('registroApellido').value;
    const carnet = document.getElementById('registroCarnet').value;
    const correo = document.getElementById('registroCorreo').value;
    const tipo_usuario = document.getElementById('registroTipo').value;

    if (!nombre || !apellido || !carnet || !correo || !tipo_usuario) {
        showToast('Por favor, complete todos los campos', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/registro`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre, apellido, carnet, correo, tipo_usuario })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Usuario registrado exitosamente', 'success');
            toggleSections(elements.registerSection, elements.loginSection);
            // Limpiar formulario
            elements.registerForm.reset();
        } else {
            showToast(data.error || 'Error al registrar usuario', 'error');
        }
    } catch (error) {
        console.error('Error en registro:', error);
        showToast('Error de conexión', 'error');
    }
}

function handleLogout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('currentUser');
    state.currentUser = null;
    showLogin();
    showToast('Sesión cerrada', 'info');
}

// Navegación
function navigateTo(section) {
    state.currentSection = section;

    // Actualizar navegación activa
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`.nav-link[data-section="${section}"]`);
    if (activeLink) activeLink.classList.add('active');

    // Mostrar sección correspondiente
    switch (section) {
        case 'inicio':
            showSection(elements.inicioSection);
            loadDashboard();
            break;
        case 'libros':
            showSection(elements.librosSection);
            loadLibros();
            break;
        case 'prestamos':
            showSection(elements.prestamosSection);
            loadPrestamos();
            break;
        case 'devoluciones':
            showSection(elements.devolucionesSection);
            loadDevoluciones();
            break;
        case 'reservas':
            showSection(elements.reservasSection);
            loadReservas();
            break;
        case 'usuarios':
            if (state.currentUser?.tipo_usuario === 'ADMINISTRADOR') {
                showSection(elements.usuariosSection);
                loadUsuarios();
            } else {
                showToast('Acceso denegado', 'error');
            }
            break;
        case 'mis-libros':
            showSection(elements.misLibrosSection);
            loadMisLibros();
            break;
        case 'reportes':
            if (state.currentUser?.tipo_usuario === 'ADMINISTRADOR') {
                showSection(elements.reportesSection);
                loadReportes();
            } else {
                showToast('Acceso denegado', 'error');
            }
            break;
    }
}

function showLogin() {
    toggleSections(elements.inicioSection, elements.loginSection);
    elements.loginSection.style.display = 'block';
    elements.registerSection.style.display = 'none';
    elements.userInfo.style.display = 'none';
    document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
}

function showMainApp() {
    elements.loginSection.style.display = 'none';
    elements.registerSection.style.display = 'none';
    elements.userInfo.style.display = 'flex';
    elements.userName.textContent = `${state.currentUser.nombre} ${state.currentUser.apellido}`;
    elements.userRole.textContent = state.currentUser.tipo_usuario;

    // Mostrar/ocultar elementos según rol
    if (state.currentUser.tipo_usuario === 'ADMINISTRADOR') {
        document.body.classList.add('is-admin');
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'inline-flex');
    } else {
        document.body.classList.remove('is-admin');
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
    }

    navigateTo('inicio');
}

function showSection(section) {
    // Ocultar todas las secciones
    const sections = [
        elements.inicioSection,
        elements.librosSection,
        elements.prestamosSection,
        elements.devolucionesSection,
        elements.reservasSection,
        elements.usuariosSection,
        elements.misLibrosSection,
        elements.reportesSection
    ];

    sections.forEach(sec => {
        if (sec !== section) sec.style.display = 'none';
    });

    section.style.display = 'block';
}

function toggleSections(hide, show) {
    hide.style.display = 'none';
    show.style.display = 'block';
}

// Dashboard
async function loadDashboard() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/estadisticas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();

            elements.totalLibros.textContent = data.total_libros;
            elements.totalUsuarios.textContent = data.total_usuarios;
            elements.prestamosActivos.textContent = data.prestamos_activos;
            elements.reservasActivas.textContent = data.reservas_activas;

            const isLector = state.currentUser?.tipo_usuario !== 'ADMINISTRADOR';
            const usuariosCard = document.getElementById('usuariosStatCard');
            if (usuariosCard) {
                usuariosCard.style.display = isLector ? 'none' : 'block';
            }

            // Mostrar libros más prestados si es admin
            if (state.currentUser?.tipo_usuario === 'ADMINISTRADOR') {
                elements.adminSection.style.display = 'block';
                renderLibrosMasPrestados(data.libros_mas_prestados);
            } else {
                elements.adminSection.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error cargando dashboard:', error);
    }
}

function renderLibrosMasPrestados(libros) {
    elements.librosMasPrestados.innerHTML = '';

    if (libros.length === 0) {
        elements.librosMasPrestados.innerHTML = '<p class="empty-state">No hay datos de préstamos</p>';
        return;
    }

    libros.forEach(libro => {
        const div = document.createElement('div');
        div.className = 'stat-card';
        div.innerHTML = `
            <div class="stat-info">
                <h3>${libro.titulo}</h3>
                <p>${libro.total_prestamos} préstamos</p>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: ${Math.min((libro.total_prestamos / Math.max(...libros.map(l => l.total_prestamos))) * 100, 100)}%"></div>
            </div>
        `;
        elements.librosMasPrestados.appendChild(div);
    });
}

// Libros
async function loadLibros() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/libros`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.libros = data.libros;
            renderLibros();
        }
    } catch (error) {
        console.error('Error cargando libros:', error);
    }
}

function renderLibros() {
    elements.librosList.innerHTML = '';

    if (state.libros.length === 0) {
        elements.booksEmptyState.style.display = 'block';
        return;
    }

    elements.booksEmptyState.style.display = 'none';

    state.libros.forEach(libro => {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <h3>${libro.titulo}</h3>
            <div class="author">${libro.autor}</div>
            <div class="info">
                <i class="fas fa-tags"></i> ${libro.categoria || 'Sin categoría'}
            </div>
            <div class="info">
                <i class="fas fa-copy"></i> ${libro.ejemplares_disponibles}/${libro.ejemplares_totales} disponibles
            </div>
            <div class="info">
                <i class="fas fa-calendar"></i> ${libro.anio_publicacion || 'Sin año'}
            </div>
            <div class="availability ${libro.ejemplares_disponibles > 0 ? 'available' : 'unavailable'}">
                <i class="fas fa-circle"></i>
                ${libro.ejemplares_disponibles > 0 ? 'Disponible' : 'No disponible'}
            </div>
            <div class="card-actions">
                <button class="btn btn-primary btn-small" onclick="verLibro(${libro.id_libro})">
                    <i class="fas fa-eye"></i> Ver
                </button>
                ${libro.ejemplares_disponibles > 0 ? (
                    state.currentUser?.tipo_usuario === 'ADMINISTRADOR' ? `
                        <button class="btn btn-secondary btn-small" onclick="reservarLibro(${libro.id_libro})">
                            <i class="fas fa-calendar-plus"></i> Reservar
                        </button>
                    ` : `
                        <button class="btn btn-success btn-small" onclick="abrirPrestarseModal(${libro.id_libro})">
                            <i class="fas fa-exchange-alt"></i> Prestarse
                        </button>
                        <button class="btn btn-secondary btn-small" onclick="reservarLibro(${libro.id_libro})">
                            <i class="fas fa-calendar-plus"></i> Reservar
                        </button>
                    `
                ) : ''}
                ${state.currentUser?.tipo_usuario === 'ADMINISTRADOR' ? `
                    <button class="btn btn-warning btn-small" onclick="editarLibro(${libro.id_libro})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-danger btn-small" onclick="eliminarLibro(${libro.id_libro})">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
                ` : ''}
            </div>
        `;
        elements.librosList.appendChild(card);
    });
}

function filterLibros() {
    const titulo = elements.searchTitulo.value.toLowerCase();
    const autor = elements.searchAutor.value.toLowerCase();
    const categoria = elements.searchCategoria.value;
    const disponible = elements.searchDisponible.checked;

    const filtered = state.libros.filter(libro => {
        const matchesTitulo = !titulo || libro.titulo.toLowerCase().includes(titulo);
        const matchesAutor = !autor || libro.autor.toLowerCase().includes(autor);
        const matchesCategoria = !categoria || libro.categoria === categoria;
        const matchesDisponible = !disponible || libro.ejemplares_disponibles > 0;

        return matchesTitulo && matchesAutor && matchesCategoria && matchesDisponible;
    });

    elements.librosList.innerHTML = '';

    if (filtered.length === 0) {
        elements.booksEmptyState.style.display = 'block';
        return;
    }

    elements.booksEmptyState.style.display = 'none';

    filtered.forEach(libro => {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <h3>${libro.titulo}</h3>
            <div class="author">${libro.autor}</div>
            <div class="info">
                <i class="fas fa-tags"></i> ${libro.categoria || 'Sin categoría'}
            </div>
            <div class="info">
                <i class="fas fa-copy"></i> ${libro.ejemplares_disponibles}/${libro.ejemplares_totales} disponibles
            </div>
            <div class="info">
                <i class="fas fa-calendar"></i> ${libro.anio_publicacion || 'Sin año'}
            </div>
            <div class="availability ${libro.ejemplares_disponibles > 0 ? 'available' : 'unavailable'}">
                <i class="fas fa-circle"></i>
                ${libro.ejemplares_disponibles > 0 ? 'Disponible' : 'No disponible'}
            </div>
            <div class="card-actions">
                <button class="btn btn-primary btn-small" onclick="verLibro(${libro.id_libro})">
                    <i class="fas fa-eye"></i> Ver
                </button>
                ${libro.ejemplares_disponibles > 0 ? (
                    state.currentUser?.tipo_usuario === 'ADMINISTRADOR' ? `
                        <button class="btn btn-secondary btn-small" onclick="reservarLibro(${libro.id_libro})">
                            <i class="fas fa-calendar-plus"></i> Reservar
                        </button>
                    ` : `
                        <button class="btn btn-success btn-small" onclick="abrirPrestarseModal(${libro.id_libro})">
                            <i class="fas fa-exchange-alt"></i> Prestarse
                        </button>
                        <button class="btn btn-secondary btn-small" onclick="reservarLibro(${libro.id_libro})">
                            <i class="fas fa-calendar-plus"></i> Reservar
                        </button>
                    `
                ) : ''}
                ${state.currentUser?.tipo_usuario === 'ADMINISTRADOR' ? `
                    <button class="btn btn-warning btn-small" onclick="editarLibro(${libro.id_libro})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-danger btn-small" onclick="eliminarLibro(${libro.id_libro})">
                        <i class="fas fa-trash"></i> Eliminar
                    </button>
                ` : ''}
            </div>
        `;
        elements.librosList.appendChild(card);
    });
}

// Préstamos
async function loadPrestamos() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/prestamos`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.prestamos = data.prestamos;
            renderPrestamos();
        }
    } catch (error) {
        console.error('Error cargando préstamos:', error);
    }
}

function renderPrestamos() {
    elements.prestamosList.innerHTML = '';

    if (state.prestamos.length === 0) {
        elements.prestamosList.innerHTML = '<div class="empty-state"><i class="fas fa-exchange-alt icon"></i><h3>No hay préstamos</h3><p>No se han registrado préstamos</p></div>';
        return;
    }

    const isLector = state.currentUser?.tipo_usuario !== 'ADMINISTRADOR';
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                ${!isLector ? '<th>Usuario</th>' : ''}
                <th>Libro</th>
                <th>Fecha Préstamo</th>
                <th>Fecha Vencimiento</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            ${state.prestamos.map(p => `
                <tr>
                    ${!isLector ? `<td>${p.usuario}</td>` : ''}
                    <td>${p.libro}</td>
                    <td>${formatDate(p.fecha_prestamo)}</td>
                    <td>${formatDate(p.fecha_vencimiento)}</td>
                    <td><span class="status-badge ${p.estado.toLowerCase()}">${p.estado}</span></td>
                    <td class="action-buttons">
                        ${p.estado === 'PRESTADO' && !isLector ? `
                            <button class="btn btn-success btn-small" onclick="registrarDevolucion(${p.id_prestamo})">
                                <i class="fas fa-undo"></i> Devolver
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary btn-small" onclick="verPrestamo(${p.id_prestamo})">
                            <i class="fas fa-eye"></i> Ver
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    elements.prestamosList.appendChild(table);
}

function filterPrestamos() {
    const estado = elements.filterPrestamoEstado.value;

    const filtered = state.prestamos.filter(p => {
        return !estado || p.estado === estado;
    });

    elements.prestamosList.innerHTML = '';

    if (filtered.length === 0) {
        elements.prestamosList.innerHTML = '<div class="empty-state"><i class="fas fa-exchange-alt icon"></i><h3>No hay préstamos</h3><p>No se encontraron préstamos con ese estado</p></div>';
        return;
    }

    const isLector = state.currentUser?.tipo_usuario !== 'ADMINISTRADOR';
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                ${!isLector ? '<th>Usuario</th>' : ''}
                <th>Libro</th>
                <th>Fecha Préstamo</th>
                <th>Fecha Vencimiento</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            ${filtered.map(p => `
                <tr>
                    ${!isLector ? `<td>${p.usuario}</td>` : ''}
                    <td>${p.libro}</td>
                    <td>${formatDate(p.fecha_prestamo)}</td>
                    <td>${formatDate(p.fecha_vencimiento)}</td>
                    <td><span class="status-badge ${p.estado.toLowerCase()}">${p.estado}</span></td>
                    <td class="action-buttons">
                        ${p.estado === 'PRESTADO' && !isLector ? `
                            <button class="btn btn-success btn-small" onclick="registrarDevolucion(${p.id_prestamo})">
                                <i class="fas fa-undo"></i> Devolver
                            </button>
                        ` : ''}
                        <button class="btn btn-secondary btn-small" onclick="verPrestamo(${p.id_prestamo})">
                            <i class="fas fa-eye"></i> Ver
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    elements.prestamosList.appendChild(table);
}

// Devoluciones
async function loadDevoluciones() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/devoluciones`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.devoluciones = data.devoluciones;
            renderDevoluciones();
        }
    } catch (error) {
        console.error('Error cargando devoluciones:', error);
    }
}

function renderDevoluciones() {
    elements.devolucionesList.innerHTML = '';

    if (state.devoluciones.length === 0) {
        elements.devolucionesList.innerHTML = '<div class="empty-state"><i class="fas fa-undo icon"></i><h3>No hay devoluciones</h3><p>No se han registrado devoluciones</p></div>';
        return;
    }

    const isLector = state.currentUser?.tipo_usuario !== 'ADMINISTRADOR';
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                ${!isLector ? '<th>Usuario</th>' : ''}
                <th>Préstamo</th>
                <th>Fecha Devolución</th>
                <th>Días de Retraso</th>
                <th>Multa Generada</th>
                <th>Estado de Multa</th>
            </tr>
        </thead>
        <tbody>
            ${state.devoluciones.map(d => `
                <tr>
                    ${!isLector ? `<td>${d.usuario || 'Desconocido'}</td>` : ''}
                    <td>${d.id_prestamo}</td>
                    <td>${formatDate(d.fecha_devolucion)}</td>
                    <td>${d.dias_retraso}</td>
                    <td>Bs. ${d.multa_generada.toFixed(2)}</td>
                    <td><span class="status-badge ${d.estado_multa.toLowerCase()}">${d.estado_multa}</span></td>
                </tr>
            `).join('')}
        </tbody>
    `;

    elements.devolucionesList.appendChild(table);
}

// Reservas
async function loadReservas() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/reservas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.reservas = data.reservas;
            renderReservas();
        }
    } catch (error) {
        console.error('Error cargando reservas:', error);
    }
}

function renderReservas() {
    elements.reservasList.innerHTML = '';

    if (state.reservas.length === 0) {
        elements.reservasList.innerHTML = '<div class="empty-state"><i class="fas fa-calendar-check icon"></i><h3>No hay reservas</h3><p>No tienes reservas activas</p></div>';
        return;
    }

    const isLector = state.currentUser?.tipo_usuario !== 'ADMINISTRADOR';
    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                ${!isLector ? '<th>Usuario</th>' : ''}
                <th>Libro</th>
                <th>Fecha Reserva</th>
                <th>Estado</th>
                <th>Posición en Lista</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            ${state.reservas.map(r => `
                <tr>
                    ${!isLector ? `<td>${r.usuario}</td>` : ''}
                    <td>${r.libro}</td>
                    <td>${formatDate(r.fecha_reserva)}</td>
                    <td><span class="status-badge ${r.estado.toLowerCase()}">${r.estado}</span></td>
                    <td>${r.posicion_lista}</td>
                    <td class="action-buttons">
                        <button class="btn btn-danger btn-small" onclick="cancelarReserva(${r.id_reserva})">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    elements.reservasList.appendChild(table);
}

// Usuarios
async function loadUsuarios() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/usuarios`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.usuarios = data.usuarios;
            renderUsuarios();
        }
    } catch (error) {
        console.error('Error cargando usuarios:', error);
    }
}

function renderUsuarios() {
    elements.usuariosList.innerHTML = '';

    if (state.usuarios.length === 0) {
        elements.usuariosList.innerHTML = '<div class="empty-state"><i class="fas fa-users icon"></i><h3>No hay usuarios</h3><p>No se han registrado usuarios</p></div>';
        return;
    }

    const table = document.createElement('table');
    table.innerHTML = `
        <thead>
            <tr>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Carnet</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            ${state.usuarios.map(u => `
                <tr>
                    <td>${u.nombre} ${u.apellido}</td>
                    <td>${u.correo}</td>
                    <td>${u.carnet}</td>
                    <td><span class="badge badge-primary">${u.tipo_usuario}</span></td>
                    <td><span class="status-badge ${u.estado.toLowerCase()}">${u.estado}</span></td>
                    <td class="action-buttons">
                        <button class="btn btn-warning btn-small" onclick="editarUsuario(${u.id_usuario})">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="btn btn-danger btn-small" onclick="eliminarUsuario(${u.id_usuario})">
                            <i class="fas fa-trash"></i> Eliminar
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;

    elements.usuariosList.appendChild(table);
}

// Categorías
async function loadCategorias() {
    try {
        const response = await fetch(`${API_BASE_URL}/categorias`);
        if (response.ok) {
            const data = await response.json();
            state.categorias = data.categorias;
            populateCategoriasSelect();
        }
    } catch (error) {
        console.error('Error cargando categorías:', error);
    }
}

function populateCategoriasSelect() {
    const selects = [elements.searchCategoria, document.getElementById('bookCategoria')];

    selects.forEach(select => {
        if (select) {
            select.innerHTML = '<option value="">Todas las categorías</option>';
            state.categorias.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id_categoria;
                option.textContent = cat.nombre;
                select.appendChild(option);
            });
        }
    });
}

// Modales
function openBookModal(id = null) {
    document.getElementById('bookModalTitle').innerHTML = `
        <i class="fas fa-book"></i> ${id ? 'Editar Libro' : 'Nuevo Libro'}
    `;
    document.getElementById('bookId').value = id || '';

    if (id) {
        const libro = state.libros.find(l => l.id_libro === id);
        if (libro) {
            document.getElementById('bookTitulo').value = libro.titulo;
            document.getElementById('bookAutor').value = libro.autor;
            document.getElementById('bookEditorial').value = libro.editorial || '';
            document.getElementById('bookISBN').value = libro.isbn;
            document.getElementById('bookCategoria').value = libro.id_categoria || '';
            document.getElementById('bookAnio').value = libro.anio_publicacion || '';
            document.getElementById('bookEjemplares').value = libro.ejemplares_totales;
            document.getElementById('bookDisponibles').value = libro.ejemplares_disponibles;
            document.getElementById('bookDescripcion').value = libro.descripcion || '';
        }
    } else {
        elements.bookForm.reset();
    }

    openModal('bookModal');
}

function openLoanModal() {
    // Cargar usuarios y libros para los selects
    loadLoanModalData();
    openModal('loanModal');
}

function openUserModal(id = null) {
    document.getElementById('userModalTitle').innerHTML = `
        <i class="fas fa-user-plus"></i> ${id ? 'Editar Usuario' : 'Nuevo Usuario'}
    `;
    document.getElementById('userId').value = id || '';

    if (id) {
        const usuario = state.usuarios.find(u => u.id_usuario === id);
        if (usuario) {
            document.getElementById('userNombre').value = usuario.nombre;
            document.getElementById('userApellido').value = usuario.apellido;
            document.getElementById('userCarnet').value = usuario.carnet;
            document.getElementById('userCorreo').value = usuario.correo;
            document.getElementById('userTipo').value = usuario.tipo_usuario;
            document.getElementById('userEstado').value = usuario.estado;
        }
    } else {
        elements.userForm.reset();
    }

    openModal('userModal');
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Funciones de acción (globales para onclick)
window.verLibro = async function (id) {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/libros/${id}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const libro = data.libro;

            const content = `
                <div class="detail-row">
                    <span class="detail-label">Título</span>
                    <span class="detail-value">${libro.titulo}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Autor</span>
                    <span class="detail-value">${libro.autor}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Editorial</span>
                    <span class="detail-value">${libro.editorial || 'No especificada'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">ISBN</span>
                    <span class="detail-value">${libro.isbn}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Categoría</span>
                    <span class="detail-value">${libro.categoria || 'Sin categoría'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Año Publicación</span>
                    <span class="detail-value">${libro.anio_publicacion || 'No especificado'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Ejemplares Totales</span>
                    <span class="detail-value">${libro.ejemplares_totales}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Ejemplares Disponibles</span>
                    <span class="detail-value">${libro.ejemplares_disponibles}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Disponibilidad</span>
                    <span class="detail-value">
                        <span class="badge ${libro.ejemplares_disponibles > 0 ? 'badge-success' : 'badge-danger'}">
                            ${libro.ejemplares_disponibles > 0 ? 'Disponible' : 'No disponible'}
                        </span>
                    </span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Descripción</span>
                    <span class="detail-value">${libro.descripcion || 'No especificada'}</span>
                </div>
            `;

            document.getElementById('bookDetailContent').innerHTML = content;
            openModal('bookDetailModal');
        }
    } catch (error) {
        console.error('Error cargando libro:', error);
    }
};

window.reservarLibro = async function (id_libro) {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/reservas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ id_libro })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Libro reservado exitosamente', 'success');
            loadReservas();
            loadLibros();
        } else {
            showToast(data.error || 'Error al reservar libro', 'error');
        }
    } catch (error) {
        console.error('Error reservando libro:', error);
        showToast('Error de conexión', 'error');
    }
};

window.editarLibro = function (id) {
    openBookModal(id);
};

window.eliminarLibro = async function (id) {
    if (!confirm('¿Está seguro de eliminar este libro?')) return;

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/libros/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showToast('Libro eliminado exitosamente', 'success');
            loadLibros();
            loadDashboard();
        } else {
            const data = await response.json();
            showToast(data.error || 'Error al eliminar libro', 'error');
        }
    } catch (error) {
        console.error('Error eliminando libro:', error);
        showToast('Error de conexión', 'error');
    }
};

window.registrarDevolucion = async function (id_prestamo) {
    if (!confirm('¿Está seguro de registrar esta devolución?')) return;

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/devoluciones`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ id_prestamo })
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Devolución registrada exitosamente', 'success');
            loadPrestamos();
            loadDevoluciones();
            loadDashboard();
        } else {
            showToast(data.error || 'Error al registrar devolución', 'error');
        }
    } catch (error) {
        console.error('Error registrando devolución:', error);
        showToast('Error de conexión', 'error');
    }
};

window.verPrestamo = function (id) {
    const prestamo = state.prestamos.find(p => p.id_prestamo === id);
    if (prestamo) {
        const content = `
            <div class="detail-row">
                <span class="detail-label">Usuario</span>
                <span class="detail-value">${prestamo.usuario}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Libro</span>
                <span class="detail-value">${prestamo.libro}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Fecha Préstamo</span>
                <span class="detail-value">${formatDate(prestamo.fecha_prestamo)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Fecha Vencimiento</span>
                <span class="detail-value">${formatDate(prestamo.fecha_vencimiento)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Estado</span>
                <span class="detail-value">
                    <span class="badge ${prestamo.estado === 'PRESTADO' ? 'badge-primary' : 'badge-success'}">
                        ${prestamo.estado}
                    </span>
                </span>
            </div>
            ${prestamo.fecha_devolucion ? `
            <div class="detail-row">
                <span class="detail-label">Fecha Devolución</span>
                <span class="detail-value">${formatDate(prestamo.fecha_devolucion)}</span>
            </div>
            ` : ''}
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                <h4>Requisitos / Documentos en Prenda:</h4>
                <div class="detail-row" style="margin-top: 0.5rem;">
                    <span class="detail-label">CI Prenda</span>
                    <span class="detail-value">${prestamo.ci_prenda || 'No registrado'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">RU Prenda</span>
                    <span class="detail-value">${prestamo.ru_prenda || 'No registrado'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Celular</span>
                    <span class="detail-value">${prestamo.celular || 'No registrado'}</span>
                </div>
            </div>
        `;
        document.getElementById('loanDetailContent').innerHTML = content;
        openModal('loanDetailModal');
    } else {
        showToast('Préstamo no encontrado', 'error');
    }
};

window.abrirPrestarseModal = function (libroId) {
    const libro = state.libros.find(l => l.id_libro === libroId);
    if (!libro) {
        showToast('Libro no encontrado', 'error');
        return;
    }
    document.getElementById('prestarseLibroId').value = libro.id_libro;
    document.getElementById('prestarseLibroTitulo').value = libro.titulo;
    document.getElementById('prestarseCI').value = state.currentUser?.carnet || '';
    document.getElementById('prestarseRU').value = '';
    document.getElementById('prestarseCelular').value = '';
    openModal('prestarseModal');
};

window.cancelarReserva = async function (id) {
    if (!confirm('¿Está seguro de cancelar esta reserva?')) return;

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/reservas/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showToast('Reserva cancelada exitosamente', 'success');
            loadReservas();
            loadLibros();
        } else {
            const data = await response.json();
            showToast(data.error || 'Error al cancelar reserva', 'error');
        }
    } catch (error) {
        console.error('Error cancelando reserva:', error);
        showToast('Error de conexión', 'error');
    }
};

window.editarUsuario = function (id) {
    openUserModal(id);
};

window.eliminarUsuario = async function (id) {
    if (!confirm('¿Está seguro de eliminar este usuario?')) return;

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/usuarios/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showToast('Usuario eliminado exitosamente', 'success');
            loadUsuarios();
            loadDashboard();
        } else {
            const data = await response.json();
            showToast(data.error || 'Error al eliminar usuario', 'error');
        }
    } catch (error) {
        console.error('Error eliminando usuario:', error);
        showToast('Error de conexión', 'error');
    }
};

// Formularios de modales
elements.bookForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('bookId').value;
    const data = {
        titulo: document.getElementById('bookTitulo').value,
        autor: document.getElementById('bookAutor').value,
        editorial: document.getElementById('bookEditorial').value,
        isbn: document.getElementById('bookISBN').value,
        id_categoria: document.getElementById('bookCategoria').value || null,
        anio_publicacion: document.getElementById('bookAnio').value || null,
        ejemplares_totales: parseInt(document.getElementById('bookEjemplares').value),
        ejemplares_disponibles: parseInt(document.getElementById('bookDisponibles').value),
        descripcion: document.getElementById('bookDescripcion').value
    };

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const url = id ? `${API_BASE_URL}/libros/${id}` : `${API_BASE_URL}/libros`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(`Libro ${id ? 'actualizado' : 'creado'} exitosamente`, 'success');
            closeModal('bookModal');
            loadLibros();
            loadDashboard();
        } else {
            showToast(result.error || `Error al ${id ? 'actualizar' : 'crear'} libro`, 'error');
        }
    } catch (error) {
        console.error('Error en formulario de libro:', error);
        showToast('Error de conexión', 'error');
    }
});

elements.loanForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        id_usuario: document.getElementById('loanUsuario').value,
        id_libro: document.getElementById('loanLibro').value,
        dias_prestamo: parseInt(document.getElementById('loanDias').value),
        ci_prenda: document.getElementById('loanCI').value,
        ru_prenda: document.getElementById('loanRU').value,
        celular: document.getElementById('loanCelular').value
    };

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/prestamos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            showToast('Préstamo registrado exitosamente', 'success');
            closeModal('loanModal');
            loadPrestamos();
            loadDashboard();
            loadLibros();
        } else {
            showToast(result.error || 'Error al registrar préstamo', 'error');
        }
    } catch (error) {
        console.error('Error en formulario de préstamo:', error);
        showToast('Error de conexión', 'error');
    }
});

elements.userForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('userId').value;
    const data = {
        nombre: document.getElementById('userNombre').value,
        apellido: document.getElementById('userApellido').value,
        carnet: document.getElementById('userCarnet').value,
        correo: document.getElementById('userCorreo').value,
        tipo_usuario: document.getElementById('userTipo').value,
        estado: document.getElementById('userEstado').value
    };

    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const url = id ? `${API_BASE_URL}/usuarios/${id}` : `${API_BASE_URL}/usuarios/registro`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            showToast(`Usuario ${id ? 'actualizado' : 'creado'} exitosamente`, 'success');
            closeModal('userModal');
            loadUsuarios();
            loadDashboard();
        } else {
            showToast(result.error || `Error al ${id ? 'actualizar' : 'crear'} usuario`, 'error');
        }
    } catch (error) {
        console.error('Error en formulario de usuario:', error);
        showToast('Error de conexión', 'error');
    }
});

// Funciones auxiliares
function loadLoanModalData() {
    // Cargar usuarios
    const usuarioSelect = document.getElementById('loanUsuario');
    usuarioSelect.innerHTML = '<option value="">Seleccione...</option>';
    state.usuarios.forEach(u => {
        const option = document.createElement('option');
        option.value = u.id_usuario;
        option.textContent = `${u.nombre} ${u.apellido} (${u.carnet})`;
        usuarioSelect.appendChild(option);
    });

    // Cargar libros disponibles
    const libroSelect = document.getElementById('loanLibro');
    libroSelect.innerHTML = '<option value="">Seleccione...</option>';
    state.libros.filter(l => l.ejemplares_disponibles > 0).forEach(l => {
        const option = document.createElement('option');
        option.value = l.id_libro;
        option.textContent = `${l.titulo} por ${l.autor}`;
        libroSelect.appendChild(option);
    });
}

function formatDate(dateString) {
    if (!dateString) return 'No especificado';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;

    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

// --- Mis Libros / Reportes (frontend listo, backend pendiente) ---
function loadMisLibros() {
    if (elements.misLibrosLeidos) elements.misLibrosLeidos.innerHTML = '';
    if (elements.misFavoritosList) elements.misFavoritosList.innerHTML = '';
    if (elements.misLibrosEmpty) elements.misLibrosEmpty.style.display = 'block';
}

function loadReportes() {
    if (elements.reportesList) elements.reportesList.innerHTML = '';
    if (elements.reportesEmpty) elements.reportesEmpty.style.display = 'block';
}

if (elements.refreshMisLibros) {
    elements.refreshMisLibros.addEventListener('click', loadMisLibros);
}
if (elements.refreshReports) {
    elements.refreshReports.addEventListener('click', loadReportes);
}
if (elements.downloadPdfBtn) {
    elements.downloadPdfBtn.addEventListener('click', () => {
        showToast('Función de reportes en desarrollo', 'info');
    });
}
if (elements.downloadExcelBtn) {
    elements.downloadExcelBtn.addEventListener('click', () => {
        showToast('Función de reportes en desarrollo', 'info');
    });
}
