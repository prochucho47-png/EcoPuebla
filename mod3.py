import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'(Hola,\s*<strong>\{\{\s*username\s*\}\}</strong>)', re.IGNORECASE)

new_text = r'\1\n            | <a href="/mis_descubrimientos" class="nav-link">📸 Mis Descubrimientos</a>'

content = pattern.sub(new_text, content)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
