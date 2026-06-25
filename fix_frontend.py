import re

path = "frontend/js/app.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Agregar elementos faltantes al objeto `elements`
old1 = """    // Toast
    toast: document.getElementById('toast')
};"""
new1 = """    // Toast
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
};"""
assert old1 in content, "ANCHOR 1 NO ENCONTRADO"
content = content.replace(old1, new1)

# 2. Agregar los case 'mis-libros' y 'reportes' al switch de navegación
old2 = """        case 'usuarios':
            if (state.currentUser?.tipo_usuario === 'ADMINISTRADOR') {
                showSection(elements.usuariosSection);
                loadUsuarios();
            } else {
                showToast('Acceso denegado', 'error');
            }
            break;
    }
}"""
new2 = """        case 'usuarios':
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
}"""
assert old2 in content, "ANCHOR 2 NO ENCONTRADO"
content = content.replace(old2, new2)

# 3. Agregar las secciones nuevas al arreglo de showSection (para que se oculten/muestren bien)
old3 = """    const sections = [
        elements.inicioSection,
        elements.librosSection,
        elements.prestamosSection,
        elements.devolucionesSection,
        elements.reservasSection,
        elements.usuariosSection
    ];"""
new3 = """    const sections = [
        elements.inicioSection,
        elements.librosSection,
        elements.prestamosSection,
        elements.devolucionesSection,
        elements.reservasSection,
        elements.usuariosSection,
        elements.misLibrosSection,
        elements.reportesSection
    ];"""
assert old3 in content, "ANCHOR 3 NO ENCONTRADO"
content = content.replace(old3, new3)

# 4. Agregar funciones stub al final del archivo (evitan crash, muestran estado vacío)
stub = """

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
"""
content += stub

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, app.js actualizado correctamente.")
