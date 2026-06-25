path = "frontend/js/app.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

GENERIC_COVER = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='280'><rect width='200' height='280' fill='%23cbd5e1'/><text x='100' y='130' font-size='40' text-anchor='middle' fill='%23475569'>📚</text><text x='100' y='170' font-size='13' text-anchor='middle' fill='%23475569'>Sin portada</text></svg>"

# 1. Insertar la constante una sola vez, antes de "const elements = {"
old_anchor = "const elements = {"
new_const = f'const GENERIC_COVER_URL = "{GENERIC_COVER}";\n\n{old_anchor}'
assert content.count(old_anchor) >= 1, "ANCHOR DE elements NO ENCONTRADO"
content = content.replace(old_anchor, new_const, 1)

# 2. Reemplazar las dos tarjetas rotas para que usen la constante en vez del SVG inline
broken = f"<img src=\"${{libro.portada_url || '{GENERIC_COVER}'}}\" alt=\"Portada de ${{libro.titulo}}\" class=\"book-cover\" style=\"width:100%;height:160px;object-fit:cover;border-radius:6px;margin-bottom:8px;\">"
fixed = "<img src=\"${libro.portada_url || GENERIC_COVER_URL}\" alt=\"Portada de ${libro.titulo}\" class=\"book-cover\" style=\"width:100%;height:160px;object-fit:cover;border-radius:6px;margin-bottom:8px;\">"

count = content.count(broken)
assert count == 2, f"Se esperaban 2 coincidencias rotas, se encontraron {count}"
content = content.replace(broken, fixed)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Listo, error de sintaxis corregido.")
