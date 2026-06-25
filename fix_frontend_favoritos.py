path = "frontend/js/app.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Variable global para guardar qué libros son favoritos del usuario actual
anchor_const = "const GENERIC_COVER_URL"
assert content.count(anchor_const) == 1, f"ANCHOR CONST: {content.count(anchor_const)} coincidencias"
content = content.replace(anchor_const, "let favoritosIdsSet = new Set();\n\nconst GENERIC_COVER_URL", 1)

# 2. Agregar boton de corazon en las tarjetas (aparece 2 veces, renderLibros y filterLibros)
old_card = '''<div class="card-actions">
                <button class="btn btn-primary btn-small" onclick="verLibro(${libro.id_libro})">'''
new_card = '''<div class="card-actions">
                <button class="btn btn-heart-btn btn-small" onclick="toggleFavorito(${libro.id_libro})" id="heart-${libro.id_libro}" title="Agregar a favoritos">
                    <i class="fas fa-heart" style="color:${favoritosIdsSet.has(libro.id_libro) ? '#e63946' : '#cbd5e1'}"></i>
                </button>
                <button class="btn btn-primary btn-small" onclick="verLibro(${libro.id_libro})">'''
count = content.count(old_card)
assert count == 2, f"CARD: se esperaban 2 coincidencias, se encontraron {count}"
content = content.replace(old_card, new_card)

# 3. Reemplazar la funcion loadMisLibros (placeholder) por la version real
old_stub = """function loadMisLibros() {
    if (elements.misLibrosLeidos) elements.misLibrosLeidos.innerHTML = '';
    if (elements.misFavoritosList) elements.misFavoritosList.innerHTML = '';
    if (elements.misLibrosEmpty) elements.misLibrosEmpty.style.display = 'block';
}"""

new_func = """async function loadMisLibros() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const headers = { 'Authorization': `Bearer ${token}` };
        const [favRes, leidosRes] = await Promise.all([
            fetch(`${API_BASE_URL}/favoritos?tipo=FAVORITO`, { headers }),
            fetch(`${API_BASE_URL}/favoritos?tipo=LEIDO`, { headers })
        ]);
        const favoritos = favRes.ok ? (await favRes.json()).favoritos : [];
        const leidos = leidosRes.ok ? (await leidosRes.json()).favoritos : [];

        favoritosIdsSet = new Set(favoritos.map(f => f.id_libro));

        if (elements.misFavoritosList) {
            elements.misFavoritosList.innerHTML = favoritos.length === 0
                ? '<p>No tienes favoritos aun</p>'
                : favoritos.map(f => `
                    <div class="book-card-mini">
                        <h4>${f.libro ? f.libro.titulo : 'Libro'}</h4>
                        <div class="author">${f.libro ? f.libro.autor : ''}</div>
                        <button class="btn btn-danger btn-small" onclick="toggleFavorito(${f.id_libro})">
                            <i class="fas fa-heart-broken"></i> Quitar
                        </button>
                    </div>
                `).join('');
        }
        if (elements.misLibrosLeidos) {
            elements.misLibrosLeidos.innerHTML = leidos.length === 0
                ? '<p>Aun no marcaste libros como leidos</p>'
                : leidos.map(f => `
                    <div class="book-card-mini">
                        <h4>${f.libro ? f.libro.titulo : 'Libro'}</h4>
                        <div class="author">${f.libro ? f.libro.autor : ''}</div>
                    </div>
                `).join('');
        }
        if (elements.misLibrosEmpty) {
            elements.misLibrosEmpty.style.display = (favoritos.length === 0 && leidos.length === 0) ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Error cargando mis libros:', error);
    }
}

window.toggleFavorito = async function (idLibro) {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

        if (favoritosIdsSet.has(idLibro)) {
            const response = await fetch(`${API_BASE_URL}/favoritos/${idLibro}?tipo=FAVORITO`, { method: 'DELETE', headers });
            if (response.ok) {
                favoritosIdsSet.delete(idLibro);
                showToast('Quitado de favoritos', 'success');
            }
        } else {
            const response = await fetch(`${API_BASE_URL}/favoritos`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ id_libro: idLibro, tipo: 'FAVORITO' })
            });
            if (response.ok) {
                favoritosIdsSet.add(idLibro);
                showToast('Agregado a favoritos', 'success');
            }
        }

        const btn = document.getElementById(`heart-${idLibro}`);
        if (btn) {
            const icon = btn.querySelector('i');
            icon.style.color = favoritosIdsSet.has(idLibro) ? '#e63946' : '#cbd5e1';
        }
        if (state.currentSection === 'mis-libros') loadMisLibros();
    } catch (error) {
        console.error('Error actualizando favorito:', error);
        showToast('Error de conexion', 'error');
    }
};"""

assert old_stub in content, "ANCHOR STUB loadMisLibros NO ENCONTRADO"
content = content.replace(old_stub, new_func)

# 4. Cargar el set de favoritos justo despues de iniciar sesion (para pintar corazones correctos)
anchor_login = "    navigateTo('inicio');\n}"
assert content.count(anchor_login) == 1, f"ANCHOR LOGIN: {content.count(anchor_login)} coincidencias"
content = content.replace(anchor_login, "    navigateTo('inicio');\n    loadFavoritosIdsInicial();\n}", 1)

extra_func = """

async function loadFavoritosIdsInicial() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/favoritos?tipo=FAVORITO`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            favoritosIdsSet = new Set(data.favoritos.map(f => f.id_libro));
        }
    } catch (error) {
        console.error('Error cargando favoritos iniciales:', error);
    }
}
"""
content += extra_func

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, boton de corazon y Mis Libros conectados.")
