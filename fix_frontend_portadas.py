path = "frontend/js/app.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

GENERIC_COVER = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='280'><rect width='200' height='280' fill='%23cbd5e1'/><text x='100' y='130' font-size='40' text-anchor='middle' fill='%23475569'>📚</text><text x='100' y='170' font-size='13' text-anchor='middle' fill='%23475569'>Sin portada</text></svg>"

old_snippet = '''card.innerHTML = `
            <h3>${libro.titulo}</h3>'''

new_snippet = f'''card.innerHTML = `
            <img src="${{libro.portada_url || '{GENERIC_COVER}'}}" alt="Portada de ${{libro.titulo}}" class="book-cover" style="width:100%;height:160px;object-fit:cover;border-radius:6px;margin-bottom:8px;">
            <h3>${{libro.titulo}}</h3>'''

count = content.count(old_snippet)
assert count == 2, f"Se esperaban 2 coincidencias, se encontraron {{count}}"
content = content.replace(old_snippet, new_snippet)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, portadas agregadas a las tarjetas de libros.")
