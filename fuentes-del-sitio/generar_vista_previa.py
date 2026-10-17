#!/usr/bin/env python3
"""Genera la carpeta de vista previa para el artefacto de Claude a partir de funnyfoot-sitio/.

Es una copia del sitio con estas diferencias: los enlaces son relativos a archivos
(el artefacto no sirve rutas absolutas ni carpetas), se marca como vista previa
(el checkout no envía el pedido y el panel solo funciona en modo demostración) y
se agrega vista-previa.js, que avisa que los formularios se envían a Netlify solo
en el sitio publicado.

Uso:  python3 fuentes-del-sitio/generar_vista_previa.py <carpeta_de_salida>
Después se publica <carpeta_de_salida>/index.html como artefacto, con todos los
demás archivos de la carpeta en `files`.
"""
import os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(AQUI), 'funnyfoot-sitio')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(AQUI), 'vista-previa')

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
for f in ('_headers', 'robots.txt', 'sitemap.xml'):
    os.remove(os.path.join(OUT, f))

open(os.path.join(OUT, 'assets/js/vista-previa.js'), 'w', encoding='utf-8').write("""/* Solo en la vista previa de Claude: los formularios se envían a Netlify cuando el sitio está publicado. */
document.addEventListener('submit', function (e) {
  var f = e.target;
  if (!f || !f.hasAttribute || !f.hasAttribute('data-netlify')) return;
  e.preventDefault();
  var t = document.getElementById('toast'), m = document.getElementById('toastMsg');
  if (t && m) {
    m.textContent = 'Vista previa: en el sitio publicado este formulario se envía a Netlify.';
    t.classList.add('show');
    setTimeout(function () { t.classList.remove('show'); }, 3500);
  }
}, true);
""")


def rel(target, depth):
    pre = '../' * depth
    if target == '/':
        return pre + 'index.html'
    if target.endswith('/'):
        return pre + target.lstrip('/') + 'index.html'
    return pre + target.lstrip('/')


for d, _, fs in os.walk(OUT):
    for f in fs:
        if not f.endswith('.html'):
            continue
        p = os.path.join(d, f)
        depth = len(os.path.relpath(p, OUT).split(os.sep)) - 1
        pre = '../' * depth
        s = open(p, encoding='utf-8').read()
        s = re.sub(r'\b(href|src|action)="(/[^"#?]*)"', lambda m: '%s="%s"' % (m.group(1), rel(m.group(2), depth)), s)
        meta = '<meta name="ff-base" content="/">'
        assert meta in s, p
        s = s.replace(meta, '<meta name="ff-base" content="%s">\n<meta name="ff-preview" content="1">' % pre, 1)
        tag = '<script src="%sassets/js/sitio.js" defer></script>' % pre
        if tag in s:
            s = s.replace(tag, tag + '\n<script src="%sassets/js/vista-previa.js" defer></script>' % pre, 1)
        open(p, 'w', encoding='utf-8').write(s)

print('Vista previa generada en', OUT)
print('Archivos para `files`:')
for d, _, fs in os.walk(OUT):
    for f in sorted(fs):
        r = os.path.relpath(os.path.join(d, f), OUT)
        if r != 'index.html':
            print(' ', r)
