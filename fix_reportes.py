path = "frontend/js/app.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """function loadReportes() {
    if (elements.reportesList) elements.reportesList.innerHTML = '';
    if (elements.reportesEmpty) elements.reportesEmpty.style.display = 'block';
}"""

new = """async function loadReportes() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const headers = { 'Authorization': `Bearer ${token}` };

        const [librosRes, usuariosRes, prestamosRes, devolucionesRes, reservasRes] = await Promise.all([
            fetch(`${API_BASE_URL}/libros`, { headers }),
            fetch(`${API_BASE_URL}/usuarios`, { headers }),
            fetch(`${API_BASE_URL}/prestamos`, { headers }),
            fetch(`${API_BASE_URL}/devoluciones`, { headers }),
            fetch(`${API_BASE_URL}/reservas`, { headers })
        ]);

        const libros = librosRes.ok ? (await librosRes.json()).libros : [];
        const usuarios = usuariosRes.ok ? (await usuariosRes.json()).usuarios : [];
        const prestamos = prestamosRes.ok ? (await prestamosRes.json()).prestamos : [];
        const devoluciones = devolucionesRes.ok ? (await devolucionesRes.json()).devoluciones : [];
        const reservas = reservasRes.ok ? (await reservasRes.json()).reservas : [];

        const multasPendientes = devoluciones
            .filter(d => d.estado_multa !== 'PAGADA')
            .reduce((sum, d) => sum + (d.multa_generada || 0), 0);

        if (elements.reportTotalLibros) elements.reportTotalLibros.textContent = libros.length;
        if (elements.reportTotalUsuarios) elements.reportTotalUsuarios.textContent = usuarios.length;
        if (elements.reportTotalPrestamos) elements.reportTotalPrestamos.textContent = prestamos.length;
        if (elements.reportTotalDevoluciones) elements.reportTotalDevoluciones.textContent = devoluciones.length;
        if (elements.reportTotalReservas) elements.reportTotalReservas.textContent = reservas.length;
        if (elements.reportTotalMultas) elements.reportTotalMultas.textContent = `Bs. ${multasPendientes.toFixed(2)}`;

        if (elements.reportesList) {
            elements.reportesList.innerHTML = `
                <table class="table">
                    <thead><tr><th>Métrica</th><th>Valor</th></tr></thead>
                    <tbody>
                        <tr><td>Total Libros</td><td>${libros.length}</td></tr>
                        <tr><td>Usuarios Registrados</td><td>${usuarios.length}</td></tr>
                        <tr><td>Total Préstamos</td><td>${prestamos.length}</td></tr>
                        <tr><td>Préstamos Activos</td><td>${prestamos.filter(p => p.estado === 'PRESTADO').length}</td></tr>
                        <tr><td>Total Devoluciones</td><td>${devoluciones.length}</td></tr>
                        <tr><td>Total Reservas</td><td>${reservas.length}</td></tr>
                        <tr><td>Multas Pendientes</td><td>Bs. ${multasPendientes.toFixed(2)}</td></tr>
                    </tbody>
                </table>
            `;
        }
        if (elements.reportesEmpty) elements.reportesEmpty.style.display = 'none';
    } catch (error) {
        console.error('Error cargando reportes:', error);
        if (elements.reportesEmpty) elements.reportesEmpty.style.display = 'block';
    }
}"""

assert old in content, "ANCHOR NO ENCONTRADO"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, loadReportes() actualizada con datos reales.")
