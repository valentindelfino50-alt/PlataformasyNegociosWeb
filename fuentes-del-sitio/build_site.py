#!/usr/bin/env python3
"""Genera las páginas del sitio de Funny Foot a partir de funnyfoot-sitio/datos/productos.json.

Solo usa la biblioteca estándar de Python (3.8 o superior). Se ejecuta:
  - en Netlify, como comando de build (ver netlify.toml), cada vez que el panel de administración publica cambios;
  - a mano:  python3 fuentes-del-sitio/build_site.py

Escribe en funnyfoot-sitio/: index.html, productos/, producto/, nosotros/, contacto/, checkout/,
pedido-recibido/, políticas, páginas de gracias, 404.html, sitemap.xml, robots.txt y assets/js/catalogo.js.
Los archivos fijos (estilos, scripts, imágenes, admin/) no se tocan.
"""
import html
import json
import os
import re
import shutil
import sys
import unicodedata
import urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(AQUI), 'funnyfoot-sitio')
DATA = os.path.join(SITE, 'datos', 'productos.json')

with open(DATA, encoding='utf-8') as fh:
    D = json.load(fh)
N = D['negocio']
T = D['tienda']
CATS = D.get('categorias', [])
ALL = D.get('productos', [])
BASE = N.get('sitioUrl', '').rstrip('/')
NAME = N['nombre']
TODAY = os.environ.get('FF_FECHA') or __import__('datetime').date.today().isoformat()

esc = html.escape


def slugify(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-') or 'producto'


def money(n):
    return '$' + '{:,}'.format(int(round(n))).replace(',', '.')


def num(n):
    return ('%g' % n)


def tint(hexc, amt):
    c = hexc.lstrip('#')
    if len(c) != 6:
        c = '9AA0A8'
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return 'rgb(%d,%d,%d)' % (round(r + (255 - r) * amt), round(g + (255 - g) * amt), round(b + (255 - b) * amt))


# ---------- datos normalizados ----------
CAT_BY_ID = {}
for c in CATS:
    c.setdefault('slug', slugify(c['nombre']))
    c.setdefault('h1', c['nombre'])
    c.setdefault('intro', '')
    c.setdefault('resumen', '')
    c.setdefault('icono', 'spark')
    CAT_BY_ID[c['id']] = c

PRODUCTS = []
_slugs = set()
for p in ALL:
    if not p.get('visible', True):
        continue
    p = dict(p)
    s = p.get('slug') or slugify(p['nombre'])
    if s in _slugs:
        s = '%s-%s' % (s, p['id'])
    _slugs.add(s)
    p['slug'] = s
    p['talles'] = sorted(set(int(t) for t in p.get('talles', [])))
    p['imagenes'] = list(p.get('imagenes', []))
    p['agotado'] = bool(p.get('agotado', False))
    p['led'] = bool(p.get('led', False))
    p.setdefault('color', '#9AA0A8')
    p.setdefault('colorNombre', '')
    p.setdefault('descripcion', '')
    PRODUCTS.append(p)

PRODUCT_BY_ID = {p['id']: p for p in PRODUCTS}


def cat_products(cid):
    return [p for p in PRODUCTS if p.get('categoria') == cid]


def cat_range(cid):
    ts = [t for p in cat_products(cid) for t in p['talles']]
    return (min(ts), max(ts)) if ts else (None, None)


def p_url(p):
    return '/producto/%s/' % p['slug']


def c_url(c):
    return '/productos/%s/' % c['slug']


def abs_url(path):
    return BASE + path


SPRITE = open(os.path.join(AQUI, 'sprite.svg.html'), encoding='utf-8').read()
_NUEVOS = open(os.path.join(AQUI, 'iconos-nuevos.svg.html'), encoding='utf-8').read()
SPRITE = SPRITE.replace('</defs>', _NUEVOS + '</defs>', 1)

# Los valores de "icono" que ya están guardados en el catálogo se conservan: cada uno se dibuja con una ilustración propia.
CAT_ART = {'spark': 'ic-shoe-led', 'shield': 'ic-boot', 'heart': 'ic-shoe', 'star': 'ic-shoe-sport', 'shirt': 'ic-sandal', 'users': 'ic-shoe'}


def cat_art(c):
    return CAT_ART.get((c or {}).get('icono'), 'ic-shoe')


def prod_art(p):
    cat = CAT_BY_ID.get(p.get('categoria'))
    art = cat_art(cat)
    if art == 'ic-boot':
        return 'ic-boot'
    if p['led']:
        return 'ic-shoe-led'
    return art if art in ('ic-shoe-sport', 'ic-sandal') else 'ic-shoe'

ICON_X = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><line x1="4" y1="4" x2="20" y2="20"/><line x1="20" y1="4" x2="4" y2="20"/></svg>'
ICON_PLUS = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>'
ICON_CART = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="21" r="1.4"/><circle cx="18" cy="21" r="1.4"/><path d="M2.5 3h2.4l2.6 12.4a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 2-1.6L21 7H6.2"/></svg>'
ICON_BURGER = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>'
ICON_WA = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 20l1.3-4A8 8 0 1 1 9 19l-5 1Z"/><path d="M8.5 9.7c0 3.4 2.8 6.2 6.2 6.2"/></svg>'


def ic(name, cls='ic'):
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true"><use href="#ic-%s"/></svg>' % (cls, name)


def wa_link():
    return 'https://wa.me/%s' % N['whatsapp']


# ---------- plantilla ----------
def local_business_ld():
    ld = {
        '@context': 'https://schema.org', '@type': 'ShoeStore', 'name': NAME, 'url': abs_url('/'),
        'logo': abs_url('/assets/img/logo-funny-foot-rosa.png'), 'image': abs_url('/assets/img/og-funny-foot.png'),
        'telephone': '+' + N['whatsapp'],
        'address': {'@type': 'PostalAddress', 'streetAddress': N['direccion1'], 'addressLocality': 'Caballito',
                    'addressRegion': 'Ciudad Autónoma de Buenos Aires', 'addressCountry': 'AR'},
    }
    if N.get('email'):
        ld['email'] = N['email']
    return ld


def head(title, desc, path, robots='index,follow,max-image-preview:large', ld=None, og_image=None):
    url = abs_url(path)
    ld_html = ''.join('<script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False) for x in (ld or []))
    og_image = og_image or abs_url('/assets/img/og-funny-foot.png')
    return '''<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="%(robots)s">
<meta name="ff-base" content="/">
<link rel="canonical" href="%(url)s">
<meta name="theme-color" content="#ED0B6F">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_AR">
<meta property="og:site_name" content="%(site)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(img)s">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/estilos.css">
%(ld)s</head>
''' % dict(title=esc(title), desc=esc(desc), robots=robots, url=url, site=esc(NAME), img=esc(og_image), ld=ld_html)


def announce():
    items = []
    if T.get('envioGratisDesde'):
        items.append(('truck', 'Envío gratis desde %s' % money(T['envioGratisDesde'])))
    if T.get('cuotasSinInteres', 0) >= 2 and T.get('metodosPago', {}).get('tarjeta'):
        items.append(('card', '%d cuotas sin interés' % T['cuotasSinInteres']))
    if T.get('descuentoTransferencia') and T.get('metodosPago', {}).get('transferencia'):
        items.append(('spark', '%s%% OFF por transferencia' % num(T['descuentoTransferencia'])))
    barrio = N['direccion2'].split(',')[0].strip()
    items.append(('map', 'Retiro sin cargo en %s' % barrio))
    return '<div class="announce"><div class="wrap announce-in">%s</div></div>' % ''.join(
        '<span>%s%s</span>' % (ic(i, 'ic'), esc(t)) for i, t in items)


def header(active):
    items = [('inicio', '/', 'Inicio'), ('productos', '/productos/', 'Productos'), ('nosotros', '/nosotros/', 'Nosotros'), ('contacto', '/contacto/', 'Contacto')]
    act = ' aria-current="page" class="active"'

    def links():
        return ''.join('<a href="%s"%s>%s</a>' % (u, act if k == active else '', t) for k, u, t in items)
    return '''<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
%(ann)s
<header class="site">
  <div class="wrap bar">
    <a href="/" class="brandmark" aria-label="%(n)s - Inicio">
      <img src="/assets/img/logo-funny-foot-rosa.png" alt="%(n)s" width="76" height="34">
    </a>
    <nav class="primary" aria-label="Navegación principal">%(l)s</nav>
    <div class="header-actions">
      <button type="button" class="icon-btn hamburger" id="hamburgerBtn" aria-label="Abrir menú" aria-expanded="false" aria-controls="mobileNav">%(burger)s</button>
      <button type="button" class="icon-btn" id="cartBtn" aria-label="Ver carrito">%(cart)s<span class="cart-count" id="cartCount" hidden>0</span></button>
    </div>
  </div>
</header>
<div id="mobileNav">%(l)s</div>
''' % dict(n=esc(NAME), l=links(), burger=ICON_BURGER, cart=ICON_CART, ann=announce())


def footer_tpl():
    return '''
<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="brandmark"><img src="/assets/img/logo-funny-foot-blanco.png" alt="%(n)s" width="67" height="30" loading="lazy"></div>
        <p class="desc">Calzado infantil con estilo, calidad y mucha diversión. Local de barrio en Caballito, pedidos online para toda la Argentina.</p>
        <div class="social-row">
          <a href="%(wa)s" target="_blank" rel="noopener" aria-label="Escribinos por WhatsApp" data-wa>%(iwa)s</a>
        </div>
      </div>
      <div>
        <h4>TIENDA</h4>
        <ul>
          <li><a href="/productos/">Todos los productos</a></li>
          %(cats)s
        </ul>
      </div>
      <div>
        <h4>AYUDA</h4>
        <ul>
          <li><a href="/contacto/">Contacto</a></li>
          <li><a href="/preguntas-frecuentes/">Preguntas frecuentes</a></li>
          <li><a href="/envios-y-pagos/">Envíos y pagos</a></li>
          <li><a href="/cambios-y-devoluciones/">Cambios y devoluciones</a></li>
          <li><a href="/privacidad-y-terminos/">Privacidad y términos</a></li>
        </ul>
      </div>
      <div>
        <h4>VISITANOS</h4>
        <ul>
          <li><a href="/nosotros/">%(d1)s, %(d2)s</a></li>
          <li><a href="/nosotros/">%(hor)s</a></li>
          <li><a href="%(wa)s" target="_blank" rel="noopener" data-wa>WhatsApp %(tel)s</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span id="copyAdmin">© 2026 %(n)s. Todos los derechos reservados.</span>
      <span>Sitio desarrollado como parte de un trabajo práctico — Plataformas y Negocios Web</span>
    </div>
  </div>
</footer>

<a class="wa-float" href="%(wa)s" target="_blank" rel="noopener" data-wa aria-label="Escribinos por WhatsApp">%(iwa)s<span>WhatsApp</span></a>

<div id="toast" role="status" aria-live="polite"><span class="dot"></span><span id="toastMsg">¡Agregado al carrito!</span></div>

<div class="overlay" id="overlay"></div>
<aside class="drawer" id="cartDrawer" aria-label="Carrito de compras" aria-hidden="true">
  <div class="drawer-head">
    <h2>Tu carrito</h2>
    <button type="button" class="modal-close" id="closeDrawer" aria-label="Cerrar carrito">%(x)s</button>
  </div>
  <div class="drawer-body" id="drawerBody"></div>
  <div class="drawer-foot" id="drawerFoot"></div>
</aside>

%(sprite)s
<script src="/assets/js/config.js"></script>
<script src="/assets/js/catalogo.js"></script>
<script src="/assets/js/sitio.js" defer></script>
%(extra)s</body>
</html>
'''


def page(path, title, desc, active, body, robots='index,follow,max-image-preview:large', ld=None, body_attr='',
         with_feedback=True, extra_js='', og_image=None):
    out = head(title, desc, path, robots, ld, og_image) + header(active)
    out = out.replace('<body>', '<body%s>' % body_attr, 1)
    out += '<main id="contenido">\n' + body + '\n</main>\n'
    foot = footer_tpl() % dict(n=esc(NAME), wa=wa_link(), iwa=ICON_WA, cats=cat_links_html(), d1=esc(N['direccion1']),
                           d2=esc(N['direccion2']), hor=esc(N['horarios']), tel=esc(N['telefonoVisible']),
                           x=ICON_X, sprite=SPRITE, extra=extra_js)
    return out + foot


def cat_links_html():
    return ''.join('<li><a href="%s">%s</a></li>' % (c_url(c), esc(c['nombre'])) for c in CATS)




def write(path, content):
    if path.endswith('.html'):
        full = os.path.join(SITE, path.lstrip('/'))
    else:
        full = os.path.join(SITE, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as fh:
        fh.write(content)


# ---------- componentes ----------
def card(p, h='h3'):
    sizes = ''.join('<option value="%d">Talle %d</option>' % (s, s) for s in p['talles'])
    chips = ''
    if p['led']:
        chips += '<span class="led-chip"><svg width="10" height="10" viewBox="0 0 24 24" aria-hidden="true"><use href="#ic-spark"/></svg>LED</span>'
    if p['agotado']:
        chips += '<span class="sold-chip">Agotado</span>'
    if p['imagenes']:
        media = '<a class="card-media has-img" href="%s" aria-label="Ver %s">%s<img src="/%s" alt="%s" loading="lazy" decoding="async"></a>' % (
            p_url(p), esc(p['nombre']), chips, esc(p['imagenes'][0]), esc(p['nombre']))
    else:
        media = '<a class="card-media art" style="--tint:%s" href="%s" aria-label="Ver %s">%s<svg style="--c:%s;color:%s" role="img" aria-label="Ilustración de zapatilla %s"><use href="#%s"/></svg></a>' % (
            tint(p['color'], .8), p_url(p), esc(p['nombre']), chips, esc(p['color']), esc(p['color']), esc(p['colorNombre'].lower()), prod_art(p))
    meta = ' · '.join(x for x in [p['colorNombre'], ('Talles %d–%d' % (p['talles'][0], p['talles'][-1])) if p['talles'] else ''] if x)
    cuotas = ''
    n = T.get('cuotasSinInteres', 0)
    if n >= 2 and T.get('metodosPago', {}).get('tarjeta'):
        cuotas = '<span class="cuotas">%d cuotas de %s</span>' % (n, money(p['precio'] / n))
    if p['agotado'] or not p['talles']:
        foot = '<div class="card-foot one"><a class="btn btn-ghost-pink btn-sm btn-block" href="%s">Ver producto</a></div>' % p_url(p)
    else:
        foot = '''<div class="card-foot">
    <label class="sr-only" for="size-%(id)d">Talle de %(n)s</label>
    <select class="size-select" id="size-%(id)d"><option value="">Talle</option>%(sizes)s</select>
    <button type="button" class="add-btn" data-add="%(id)d" aria-label="Agregar %(n)s al carrito"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><use href="#ic-cart-plus"/></svg><span>Agregar</span></button>
  </div>''' % dict(id=p['id'], n=esc(p['nombre']), sizes=sizes)
    return '''<article class="card-product" data-id="%(id)d" data-name="%(dn)s">
  %(media)s
  <div class="card-body">
    <%(h)s><a href="%(url)s">%(n)s</a></%(h)s>
    <div class="card-meta"><span>%(meta)s</span></div>
    <div class="price-row"><span class="price">%(price)s</span>%(cuotas)s</div>
  </div>
  %(foot)s
</article>''' % dict(id=p['id'], dn=esc(p['nombre'].lower()), media=media, h=h, url=p_url(p), n=esc(p['nombre']),
                     meta=esc(meta), price=money(p['precio']), cuotas=cuotas, foot=foot)


def pagehead(h1, intro, crumbs=None):
    cr = ''
    if crumbs:
        parts = []
        for label, url in crumbs:
            parts.append('<a href="%s">%s</a>' % (url, esc(label)) if url else '<span aria-current="page">%s</span>' % esc(label))
        cr = '<nav class="crumbs" aria-label="Migas de pan">' + ' <span aria-hidden="true">›</span> '.join(parts) + '</nav>'
    intro_html = '<p>%s</p>' % esc(intro) if intro else ''
    return '''<div class="page-band"><div class="wrap">
  <div class="page-head">
    %s
    <div class="dashline" style="margin-bottom:16px;"><span></span><span></span><span></span></div>
    <h1>%s</h1>
    %s
  </div>
</div></div>''' % (cr, esc(h1), intro_html)


def breadcrumb_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_url(u)} for i, (n, u) in enumerate(items)]}


def listing(active_cat):
    chips = '<a class="chip-filter%s" href="/productos/">Todas</a>' % (' active' if active_cat is None else '')
    for c in CATS:
        chips += '<a class="chip-filter%s" href="%s">%s</a>' % (' active' if c is active_cat else '', c_url(c), esc(c['nombre']))
    ps = PRODUCTS if active_cat is None else cat_products(active_cat['id'])
    grid = '\n'.join(card(p, 'h2') for p in ps)
    empty = ''
    if not ps:
        empty = '<div class="empty-state">Pronto vas a encontrar productos en esta categoría. Mientras tanto, mirá <a href="/productos/" class="u">todo el catálogo</a>.</div>'
    return '''<div class="wrap">
  <div class="filter-bar" id="filterBar">%s
    <label class="sr-only" for="searchInput">Buscar por nombre</label>
    <input type="search" class="search-input" id="searchInput" placeholder="Buscar por nombre...">
  </div>
  <div class="grid-products" id="productsGrid">
%s
  </div>
  %s
  <div class="empty-state" id="emptyState" hidden>No encontramos productos con esa búsqueda. Probá con otra palabra o categoría.</div>
  <p class="note-small">Las imágenes pueden ser ilustraciones o fotos del modelo y color. Los precios y la disponibilidad de talles pueden variar; los confirmamos al recibir tu pedido.</p>
</div>''' % (chips, grid, empty)


def policy_pay_list():
    m = T.get('metodosPago', {})
    pct = T.get('descuentoTransferencia', 0)
    cuotas = T.get('cuotasSinInteres', 0)
    items = []
    if m.get('tarjeta'):
        items.append('Tarjetas de crédito y débito%s' % (', hasta %d cuotas sin interés' % cuotas if cuotas else ''))
    if m.get('mercadopago'):
        items.append('Mercado Pago (QR o link de pago)')
    if m.get('transferencia'):
        items.append('Transferencia bancaria%s' % (', con %s%% de descuento' % num(pct) if pct else ''))
    if m.get('efectivo'):
        items.append('Efectivo en el local de Caballito (con retiro en el local)')
    return items


def payment_options():
    m = T.get('metodosPago', {})
    pct = T.get('descuentoTransferencia', 0)
    cuotas = T.get('cuotasSinInteres', 0)
    out = []
    if m.get('transferencia'):
        out.append(('transferencia', 'Transferencia bancaria', ('%s%% de descuento' % num(pct)) if pct else 'Te enviamos los datos para transferir', False))
    if m.get('mercadopago'):
        out.append(('mercadopago', 'Mercado Pago', 'Te enviamos el link de pago', False))
    if m.get('tarjeta'):
        out.append(('tarjeta', 'Tarjeta de crédito o débito', ('Hasta %d cuotas sin interés. ' % cuotas if cuotas else '') + 'Coordinamos el pago con un link seguro', False))
    if m.get('efectivo'):
        out.append(('efectivo', 'Efectivo en el local', 'Solo con retiro en el local', True))
    if not out:
        out.append(('a_coordinar', 'A coordinar', 'Te contactamos para acordar el pago', False))
    return out


# ---------- páginas ----------
MAP_SVG = '''<svg viewBox="0 0 420 320" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Mapa ilustrado de Caballito con la ubicación del local">
  <rect width="420" height="320" fill="#FFF1F6"/>
  <g fill="#FFE3EF"><rect x="14" y="14" width="120" height="82" rx="10"/><rect x="154" y="14" width="96" height="82" rx="10"/><rect x="270" y="14" width="136" height="82" rx="10"/>
  <rect x="14" y="116" width="120" height="70" rx="10"/><rect x="270" y="116" width="136" height="70" rx="10"/>
  <rect x="14" y="206" width="120" height="100" rx="10"/><rect x="154" y="206" width="96" height="100" rx="10"/><rect x="270" y="206" width="136" height="100" rx="10"/></g>
  <path d="M-10 168 C90 150 190 176 430 142" fill="none" stroke="#fff" stroke-width="30" stroke-linecap="round"/>
  <path d="M-10 168 C90 150 190 176 430 142" fill="none" stroke="#ED0B6F" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>
  <g stroke="#fff" stroke-width="12" stroke-linecap="round"><path d="M144 -10V330"/><path d="M260 -10V330"/></g>
  <g fill="#D9A3BB" opacity=".9"><circle cx="70" cy="55" r="6"/><circle cx="204" cy="60" r="6"/><circle cx="340" cy="58" r="6"/><circle cx="70" cy="250" r="6"/><circle cx="330" cy="248" r="6"/></g>
  <ellipse cx="206" cy="163" rx="26" ry="9" fill="#1B1226" opacity=".18"/>
  <path d="M206 160C206 160 176 128 176 106a30 30 0 0 1 60 0c0 22-30 54-30 54Z" fill="#ED0B6F" stroke="#1B1226" stroke-width="3" stroke-linejoin="round"/>
  <circle cx="206" cy="106" r="11" fill="#fff" stroke="#1B1226" stroke-width="3"/>
</svg>'''


def pg_home():
    feat = [p for p in PRODUCTS if p.get('destacado')][:8]
    for p in PRODUCTS:
        if len(feat) >= 4:
            break
        if p not in feat:
            feat.append(p)
    feat = feat[:len(feat) - len(feat) % 4] if len(feat) > 4 else feat
    hero_cards = ''
    for i, p in enumerate(feat[:2]):
        if p['imagenes']:
            media = '<div class="hc-media has-img"><img src="/%s" alt="%s" decoding="async"></div>' % (esc(p['imagenes'][0]), esc(p['nombre']))
        else:
            media = '<div class="hc-media" style="--tint:%s"><svg style="--c:%s;color:%s" role="img" aria-label="Ilustración de zapatilla"><use href="#%s"/></svg></div>' % (
                tint(p['color'], .8), esc(p['color']), esc(p['color']), prod_art(p))
        hero_cards += '<a class="hero-card hc%d" href="%s">%s<b>%s</b><span class="hc-price">%s</span></a>' % (i + 1, p_url(p), media, esc(p['nombre']), money(p['precio']))
    cats = ''
    for i, c in enumerate(CATS):
        cps = cat_products(c['id'])
        n = len(cps)
        con_foto = [p for p in cps if p['imagenes']]
        con_foto.sort(key=lambda p: not p.get('destacado'))
        if con_foto:
            art = '<span class="cat-art photo"><span class="cat-photo"><img src="/%s" alt="" loading="lazy" decoding="async"></span></span>' % esc(con_foto[0]['imagenes'][0])
        else:
            art = '<span class="cat-art"><svg viewBox="0 0 120 80" aria-hidden="true"><use href="#%s"/></svg></span>' % cat_art(c)
        resumen = '<p>%s</p>' % esc(c['resumen']) if c.get('resumen') else ''
        cats += '''<a class="cat-tile t%d" href="%s">
      %s
      <h3>%s</h3>%s
      <span class="cat-meta"><span>%d modelo%s</span><span class="cat-go">%s</span></span></a>''' % (
            i % 4, c_url(c), art, esc(c['nombre']), resumen, n, '' if n == 1 else 's', ic('arrow', 'ic'))
    feat_html = '\n'.join(card(p) for p in feat)
    free = T.get('envioGratisDesde')
    trust = [
        ('truck', 'Envíos a todo el país', ('Gratis desde %s' % money(free)) if free else 'Por correo a todo el país'),
        ('map', 'Retiro sin cargo', 'En %s, Caballito' % esc(N['direccion1'])),
        ('card', 'Pagá como prefieras', ('Hasta %d cuotas sin interés' % T['cuotasSinInteres']) if T.get('cuotasSinInteres', 0) >= 2 and T.get('metodosPago', {}).get('tarjeta') else 'Transferencia, Mercado Pago y efectivo'),
        ('swap', 'Cambios sin vueltas', 'Hasta %d días para cambiar el talle' % T.get('diasCambio', 30)),
    ]
    trust_html = ''.join('<div class="trust-item"><span class="trust-ic">%s</span><div><b>%s</b><span>%s</span></div></div>' % (ic(i), esc(t), x) for i, t, x in trust)
    faq_home = faq_html(faq_items()[:5])
    body = '''<section class="hero">
  <div class="hero-panel"></div>
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <span class="kicker"><span class="dashline"><span></span><span></span><span></span></span>TIENDA FAMILIAR EN CABALLITO</span>
      <h1>Zapatillas que <span class="hl">iluminan</span> cada paso</h1>
      <p>Calzado infantil con estilo, comodidad y mucha diversión: modelos con luz LED, botas, zapatillas urbanas y deportivas. Del local de barrio a tu casa, en todo el país.</p>
      <div class="hero-cta">
        <a href="/productos/" class="btn btn-pink">Ver catálogo</a>
        <a href="/nosotros/" class="btn btn-outline-light">Visitanos en Caballito</a>
      </div>
    </div>
    <div class="hero-visual">
      <div class="hero-stack">%(hcards)s
        <div class="hero-badge"><img src="/assets/img/logo-funny-foot-blanco.png" alt="%(n)s" width="120" height="54"></div>
      </div>
    </div>
  </div>
</section>

<section class="trust"><div class="wrap"><div class="trust-in">%(trust)s</div></div></section>

<section class="wrap">
  <div class="section-head"><div><span class="eyebrow">Categorías</span><h2>Elegí por categoría</h2></div></div>
  <div class="cat-grid">%(cats)s</div>
</section>

<section class="wrap">
  <div class="section-head">
    <div><span class="eyebrow">Destacados</span><h2>Los que más se piden</h2><p>Algunos de los modelos que tenemos disponibles.</p></div>
    <a href="/productos/" class="btn btn-outline btn-sm">Ver todo el catálogo</a>
  </div>
  <div class="grid-products">
%(feat)s
  </div>
</section>

<section class="wrap">
  <div class="section-head"><div><span class="eyebrow">Paso a paso</span><h2>Cómo comprar</h2></div></div>
  <ol class="steps-list">
    <li><b>Elegí modelo y talle</b><span>Recorré el catálogo y sumá al carrito lo que te guste.</span></li>
    <li><b>Completá tus datos y confirmá</b><span>Elegís envío o retiro y el medio de pago. Recibís tu número de pedido.</span></li>
    <li><b>Coordinamos pago y entrega</b><span>Te contactamos para confirmar disponibilidad y acordar el pago y la entrega.</span></li>
  </ol>
</section>

<section class="wrap">
  <div class="section-head"><div><span class="eyebrow">Nuestra forma de trabajar</span><h2>Por qué elegirnos</h2></div></div>
  <div class="props-grid">
    <div class="prop">%(i1)s<h3>Calidad que dura</h3><p>Materiales resistentes pensados para el ritmo de los más chicos.</p></div>
    <div class="prop">%(i2)s<h3>Comodidad de verdad</h3><p>Modelos pensados para usar todo el día.</p></div>
    <div class="prop">%(i3)s<h3>Atención de barrio</h3><p>Te asesoramos como en el local de toda la vida, ahora también online.</p></div>
    <div class="prop">%(i4)s<h3>Diversión en cada paso</h3><p>Personajes y luces que se encienden al pisar.</p></div>
  </div>
</section>

<section class="wrap">
  <div class="section-head">
    <div><span class="eyebrow">Dudas comunes</span><h2>Preguntas frecuentes</h2></div>
    <a href="/preguntas-frecuentes/" class="btn btn-outline btn-sm">Ver todas</a>
  </div>
  <div class="faq-list">%(faq)s</div>
</section>

<section class="wrap">
  <div class="section-head"><div><span class="eyebrow">Visitanos</span><h2>Nuestro local</h2></div></div>
  <div class="store-card">
    <div class="store-info">
      <div class="store-row">%(imap)s<div><b>%(d1)s</b><span>%(d2)s</span></div></div>
      <div class="store-row">%(iclock)s<div><b>Horarios</b><span>%(hor)s</span></div></div>
      <div class="store-row">%(iphone)s<div><b>WhatsApp</b><span>%(tel)s</span></div></div>
      <div class="store-actions"><a href="%(maps)s" target="_blank" rel="noopener" class="btn btn-primary btn-sm">Cómo llegar</a><a href="/nosotros/" class="btn btn-outline btn-sm">Conocer la tienda</a></div>
    </div>
    <div class="store-map">%(map)s</div>
  </div>
</section>

<section class="wrap">
  <div class="newsletter">
    <div>
      <h2>Sumate a nuestra lista</h2>
      <p>Enterate primero de los nuevos modelos con luz y de las novedades. Podés darte de baja cuando quieras. Al suscribirte aceptás la <a href="/privacidad-y-terminos/" class="u">política de privacidad</a>.</p>
    </div>
    <form class="nl-form" name="suscripcion" method="POST" action="/gracias-suscripcion/" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="suscripcion">
      <p class="hp" aria-hidden="true"><label>No completar este campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      <label class="sr-only" for="nlEmail">Email</label>
      <input id="nlEmail" type="email" name="email" required placeholder="tu@email.com" autocomplete="email">
      <button type="submit" class="btn btn-primary">Suscribirme</button>
    </form>
  </div>
</section>''' % dict(n=esc(NAME), hcards=hero_cards, faq=faq_home, trust=trust_html, cats=cats, feat=feat_html, i1=ic('shield'), i2=ic('heart'), i3=ic('users'), i4=ic('spark'),
                     imap=ic('map'), iclock=ic('clock'), iphone=ic('phone'), d1=esc(N['direccion1']), d2=esc(N['direccion2']),
                     hor=esc(N['horarios']), tel=esc(N['telefonoVisible']), map=MAP_SVG,
                     maps='https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote('%s, %s' % (N['direccion1'], N['direccion2'])))
    return page('/', '%s | Zapatillas y calzado infantil en Caballito' % NAME.replace(' Calzados', ''),
                'Zapatillas con luz LED, botas, urbanas y deportivas para niñas y niños. Local en Caballito, pedidos online para todo el país.',
                'inicio', body, ld=[local_business_ld()])


def faq_items():
    m = T.get('metodosPago', {})
    free = T.get('envioGratisDesde')
    costo = T.get('costoEnvio')
    dias = T.get('diasCambio', 30)
    pagos = [x.rstrip('.') for x in policy_pay_list()]
    envio = T.get('plazoEnvio') or 'Te confirmamos el plazo de entrega al coordinar tu pedido.'
    envio_cost = ''
    if costo:
        envio_cost = ' El envío cuesta %s' % money(costo)
        envio_cost += (' y es gratis en compras desde %s.' % money(free)) if free else '.'
    elif free:
        envio_cost = ' El envío es gratis en compras desde %s.' % money(free)
    return [
        ('¿Cómo hago un pedido?',
         'Elegí el modelo, seleccioná el talle y sumalo al carrito. Después completá tus datos en el carrito, elegí envío o retiro y el medio de pago, y confirmá. '
         'Te llega un número de pedido y nos ponemos en contacto para confirmar la disponibilidad y coordinar el pago y la entrega.'),
        ('¿Cómo sé qué talle elegir?',
         'Medí el pie de tu hijo o hija apoyado en una hoja, de talón a dedo más largo, y sumá aproximadamente 1 cm de margen. Si te queda la duda, escribinos por WhatsApp con ese largo y te aconsejamos el talle justo. '
         'Además, si no calza bien, podés cambiarlo (ver cambios).'),
        ('¿Qué medios de pago aceptan?',
         ('Aceptamos: ' + '; '.join(pagos) + '.') if pagos else 'Coordinamos el pago con vos al confirmar el pedido.'),
        ('¿Hacen envíos a todo el país?',
         'Sí, enviamos por correo a toda la Argentina. ' + envio + envio_cost),
        ('¿Puedo retirar el pedido por el local?',
         'Sí, sin cargo. Estamos en %s, %s. Horarios: %s. Te avisamos cuando el pedido esté listo para retirar.' % (N['direccion1'], N['direccion2'], N['horarios'])),
        ('¿Puedo cambiar el talle o el modelo?',
         'Sí. Tenés hasta %d días desde que recibís el producto para pedir un cambio de talle o modelo, siempre que esté sin uso y en su caja original. Escribinos por WhatsApp y lo coordinamos.' % dias),
        ('¿Qué pasa si llega con una falla?',
         'Si el producto llega con un defecto de fabricación, nos escribís con una foto y lo cambiamos sin costo o lo resolvemos de la mejor manera para vos.'),
        ('¿Cómo funcionan las zapatillas con luz LED?',
         'Los modelos con LED se iluminan con el movimiento al pisar, sin pilas que cambiar. En cada producto vas a ver la etiqueta “LED” para identificarlos.'),
        ('¿Las fotos y los precios son los reales?',
         'Las fotos corresponden a los modelos que tenemos. Los precios y la disponibilidad de talles pueden variar, por eso los confirmamos al recibir tu pedido, antes de que pagues nada.'),
        ('¿Tienen calzado para el colegio o para uso diario?',
         'Sí, tenemos modelos urbanos y deportivos pensados para el uso diario: aguantan el recreo, la plaza y el fin de semana. Consultanos y te recomendamos según la edad y el uso.'),
    ]


def faq_html(items):
    return '\n'.join('<details class="faq-item"><summary><span>%s</span></summary><div class="faq-a"><p>%s</p></div></details>' % (esc(q), esc(a)) for q, a in items)


def pg_faq():
    items = faq_items()
    ph = pagehead('Preguntas frecuentes', 'Respondemos las dudas más comunes sobre pedidos, talles, pagos, envíos y cambios.', [('Inicio', '/'), ('Preguntas frecuentes', None)])
    body = ph + """
<section class="wrap faq-wrap">
  <div class="faq-list">
%s
  </div>
  <div class="faq-cta">
    <div><h2>¿Te quedó alguna duda?</h2><p>Escribinos y te respondemos a la brevedad.</p></div>
    <a href="%s" target="_blank" rel="noopener" class="btn btn-pink" data-wa>Consultar por WhatsApp</a>
  </div>
</section>""" % (faq_html(items), wa_link())
    ld = [{'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]},
        breadcrumb_ld([('Inicio', '/'), ('Preguntas frecuentes', '/preguntas-frecuentes/')])]
    return page('/preguntas-frecuentes/', 'Preguntas frecuentes | %s' % NAME.replace(' Calzados', ''),
                'Respuestas a las dudas más comunes: cómo comprar, talles, medios de pago, envíos, retiro y cambios en Funny Foot.',
                'inicio', body, ld=ld)


def pg_productos():
    body = pagehead('Todo nuestro calzado', 'Zapatillas con luz LED, botas, urbanas y deportivas. Elegí talle y sumalo al carrito.',
                    [('Inicio', '/'), ('Productos', None)]) + '\n' + listing(None)
    return page('/productos/', 'Calzado infantil: zapatillas, botas y deportivas | %s' % NAME.replace(' Calzados', ''),
                'Catálogo de calzado infantil: zapatillas con luz LED, botas, urbanas y deportivas. Comprá online.',
                'productos', body, ld=[breadcrumb_ld([('Inicio', '/'), ('Productos', '/productos/')])])


def pg_cat(c):
    smin, smax = cat_range(c['id'])
    desc = c.get('descripcion') or c['intro'] or c['nombre']
    desc = desc.replace('{talleMin}', str(smin) if smin else '').replace('{talleMax}', str(smax) if smax else '')
    title = c.get('titulo') or '%s | %s' % (c['nombre'], NAME.replace(' Calzados', ''))
    body = pagehead(c['h1'], c['intro'], [('Inicio', '/'), ('Productos', '/productos/'), (c['nombre'], None)]) + '\n' + listing(c)
    ld = [breadcrumb_ld([('Inicio', '/'), ('Productos', '/productos/'), (c['nombre'], c_url(c))])]
    return page(c_url(c), title, desc, 'productos', body, ld=ld)


def pg_product(p):
    cat = CAT_BY_ID.get(p.get('categoria'))
    crumbs = [('Inicio', '/'), ('Productos', '/productos/')]
    if cat:
        crumbs.append((cat['nombre'], c_url(cat)))
    crumbs.append((p['nombre'], None))
    if p['imagenes']:
        thumbs = ''
        if len(p['imagenes']) > 1:
            thumbs = '<div class="pdp-thumbs">' + ''.join(
                '<button type="button" class="pdp-thumb%s" data-thumb="/%s" aria-label="Ver foto %d"><img src="/%s" alt="" loading="lazy"></button>' % (
                    ' active' if i == 0 else '', esc(src), i + 1, esc(src)) for i, src in enumerate(p['imagenes'])) + '</div>'
        gallery = '<div class="pdp-main"><img id="pdpMain" src="/%s" alt="%s" decoding="async"></div>%s' % (esc(p['imagenes'][0]), esc(p['nombre']), thumbs)
    else:
        gallery = '<div class="pdp-main art" style="--tint:%s"><svg style="--c:%s;color:%s" role="img" aria-label="Ilustración de zapatilla"><use href="#%s"/></svg></div>' % (tint(p['color'], .8), esc(p['color']), esc(p['color']), prod_art(p))
    chips = ''
    if p['led']:
        chips += '<span class="led-chip static">LED · luz al pisar</span>'
    if p['agotado']:
        chips += '<span class="sold-chip static">Agotado</span>'
    paras = [x.strip() for x in re.split(r'\n\s*\n', p['descripcion']) if x.strip()]
    desc_html = ''.join('<p>%s</p>' % esc(x).replace('\n', '<br>') for x in paras)
    if p['agotado'] or not p['talles']:
        buy = '<div class="pdp-buy"><button type="button" class="btn btn-block" disabled>Agotado por el momento</button><p class="note-small">Escribinos por <a class="u" href="%s" target="_blank" rel="noopener" data-wa>WhatsApp</a> para consultar cuándo vuelve a estar disponible.</p></div>' % wa_link()
    else:
        sizes = ''.join('<option value="%d">Talle %d</option>' % (s, s) for s in p['talles'])
        buy = '''<div class="pdp-buy">
        <label for="size-%(id)d">Talle</label>
        <select class="size-select" id="size-%(id)d"><option value="">Elegí un talle</option>%(sizes)s</select>
        <button type="button" class="btn btn-pink btn-block" data-add="%(id)d">Agregar al carrito</button>
      </div>''' % dict(id=p['id'], sizes=sizes)
    facts = []
    if p['colorNombre']:
        facts.append('<li><b>Color</b><span>%s</span></li>' % esc(p['colorNombre']))
    if p['talles']:
        facts.append('<li><b>Talles</b><span>%d al %d</span></li>' % (p['talles'][0], p['talles'][-1]))
    if cat:
        facts.append('<li><b>Categoría</b><span><a href="%s" class="u">%s</a></span></li>' % (c_url(cat), esc(cat['nombre'])))
    shipping = ''
    if T.get('envioGratisDesde'):
        shipping = '<li>%s Envío gratis desde %s</li>' % (ic('truck'), money(T['envioGratisDesde']))
    else:
        shipping = '<li>%s Envíos a todo el país</li>' % ic('truck')
    perks = '<ul class="pdp-perks">%s<li>%s Retiro sin cargo en %s</li>%s</ul>' % (
        shipping, ic('map'), esc(N['direccion1']),
        ('<li>%s %s%% de descuento pagando por transferencia</li>' % (ic('heart'), num(T['descuentoTransferencia']))) if T.get('descuentoTransferencia') and T.get('metodosPago', {}).get('transferencia') else '')
    body = '''<div class="wrap pdp-wrap">
  %(crumbs)s
  <div class="pdp">
    <div class="pdp-gallery">%(gallery)s</div>
    <div class="pdp-info">
      <div class="pdp-chips">%(chips)s</div>
      <h1>%(n)s</h1>
      <div class="price big">%(price)s</div>
      %(desc)s
      <ul class="pdp-facts">%(facts)s</ul>
      %(buy)s
      %(perks)s
    </div>
  </div>
</div>''' % dict(
        crumbs='<nav class="crumbs" aria-label="Migas de pan">' + ' <span aria-hidden="true">›</span> '.join(
            ('<a href="%s">%s</a>' % (u, esc(l))) if u else ('<span aria-current="page">%s</span>' % esc(l)) for l, u in crumbs) + '</nav>',
        gallery=gallery, chips=chips, n=esc(p['nombre']), price=money(p['precio']), desc=desc_html,
        facts=''.join(facts), buy=buy, perks=perks)
    meta_desc = (re.sub(r'\s+', ' ', p['descripcion']).strip()[:150]) if p['descripcion'].strip() else (
        '%s%s. Comprá online en %s.' % (p['nombre'], (' · Talles %d al %d' % (p['talles'][0], p['talles'][-1])) if p['talles'] else '', NAME))
    product_ld = {
        '@context': 'https://schema.org', '@type': 'Product', 'name': p['nombre'], 'sku': 'FF-%s' % p['id'],
        'description': meta_desc,
        'offers': {'@type': 'Offer', 'url': abs_url(p_url(p)), 'priceCurrency': 'ARS', 'price': str(p['precio']),
                   'availability': 'https://schema.org/OutOfStock' if p['agotado'] else 'https://schema.org/InStock'},
    }
    if p['imagenes']:
        product_ld['image'] = [abs_url('/' + i) for i in p['imagenes']]
    ld = [product_ld, breadcrumb_ld([(l, u) for l, u in crumbs if u] + [(p['nombre'], p_url(p))])]
    og = abs_url('/' + p['imagenes'][0]) if p['imagenes'] else None
    return page(p_url(p), '%s | %s' % (p['nombre'], NAME.replace(' Calzados', '')), meta_desc, 'productos', body, ld=ld, og_image=og)


def pg_nosotros():
    body = '''%(ph)s
<section class="wrap">
  <div class="about-grid">
    <div class="about-copy">
      <p>Funny Foot nació como un local de barrio en Caballito y hoy también vive en internet. Somos una empresa familiar dedicada a vestir los pies de niñas y niños con calzado cómodo, resistente y con mucha onda.</p>
      <p>Desde las clásicas zapatillas urbanas hasta los modelos con luces LED que son furor entre los más chicos, elegimos cada modelo pensando en el uso diario: que aguanten el recreo, la plaza y el fin de semana.</p>
      <p>Seguimos atendiendo como el primer día: con nombre y apellido, aconsejando el talle justo y resolviendo cualquier cambio sin vueltas.</p>
      <a href="/productos/" class="btn btn-pink">Ver catálogo</a>
    </div>
    <div class="plaque"><img src="/assets/img/logo-funny-foot-fondo-rosa.png" alt="Logo de %(n)s" width="640" height="288" loading="lazy"></div>
  </div>
</section>
<section class="wrap">
  <div class="section-head"><h2>Lo que nos representa</h2></div>
  <div class="values-grid">
    <div class="value-card">%(i1)s<h3>Cercanía</h3><p>Trato de barrio, tanto en el local como por WhatsApp.</p></div>
    <div class="value-card">%(i2)s<h3>Calidad</h3><p>Seleccionamos marcas que resisten el uso diario de los chicos.</p></div>
    <div class="value-card">%(i3)s<h3>Diversión</h3><p>Personajes y luces que hacen del calzado algo especial.</p></div>
    <div class="value-card">%(i4)s<h3>Comunidad</h3><p>Convenios con colegios de la zona y clientas de toda la vida.</p></div>
  </div>
  <div class="callout">
    %(imap)s
    <p><b>¿Sabías que</b> trabajamos junto a colegios de Caballito para equipar a los chicos con calzado escolar y deportivo al inicio de cada ciclo lectivo? Consultanos por convenios institucionales.</p>
  </div>
</section>
<section class="wrap">
  <div class="section-head"><h2>Visitá nuestro local</h2></div>
  <div class="store-card">
    <div class="store-info">
      <div class="store-row">%(imap)s<div><b>%(d1)s</b><span>%(d2)s</span></div></div>
      <div class="store-row">%(iclock)s<div><b>Horarios</b><span>%(hor)s</span></div></div>
      <div class="store-row">%(itruck)s<div><b>Retiro en local</b><span>Sin cargo, al confirmar tu pedido</span></div></div>
      <div class="store-actions"><a href="%(maps)s" target="_blank" rel="noopener" class="btn btn-primary btn-sm">Cómo llegar</a><a href="/contacto/" class="btn btn-outline btn-sm">Escribinos</a></div>
    </div>
    <div class="store-map">%(map)s</div>
  </div>
</section>''' % dict(ph=pagehead('De un local de Caballito a tu casa', 'Conocé quiénes somos y dónde encontrarnos.'), n=esc(NAME),
                     i1=ic('users'), i2=ic('shield'), i3=ic('spark'), i4=ic('heart'), imap=ic('map'), iclock=ic('clock'), itruck=ic('truck'),
                     d1=esc(N['direccion1']), d2=esc(N['direccion2']), hor=esc(N['horarios']), map=MAP_SVG,
                     maps='https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote('%s, %s' % (N['direccion1'], N['direccion2'])))
    return page('/nosotros/', 'Nosotros | %s, local de calzado en Caballito' % NAME.replace(' Calzados', ''),
                'Funny Foot es un local familiar de calzado infantil en Caballito, Buenos Aires. Conocé nuestra historia, horarios y cómo llegar.',
                'nosotros', body, ld=[local_business_ld()])


def pg_contacto():
    email_row = ''
    if N.get('email'):
        email_row = '<div class="store-row" style="margin-top:16px;">%s<div><b>Email</b><span><a href="mailto:%s" class="u">%s</a></span></div></div>' % (ic('users'), esc(N['email']), esc(N['email']))
    body = '''%(ph)s
<section class="wrap">
  <div class="contact-grid">
    <div class="form-card">
      <h2 style="font-size:20px;margin-bottom:18px;">Envianos un mensaje</h2>
      <form name="contacto" method="POST" action="/gracias/" data-netlify="true" netlify-honeypot="bot-field">
        <input type="hidden" name="form-name" value="contacto">
        <p class="hp" aria-hidden="true"><label>No completar este campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
        <div class="field"><label for="cName">Nombre</label><input id="cName" name="nombre" required maxlength="80" autocomplete="name" placeholder="Tu nombre"></div>
        <div class="field"><label for="cEmail">Email</label><input id="cEmail" name="email" type="email" required autocomplete="email" placeholder="tu@email.com"></div>
        <div class="field"><label for="cTel">Teléfono (opcional)</label><input id="cTel" name="telefono" type="tel" maxlength="30" autocomplete="tel" placeholder="11 0000-0000"></div>
        <div class="field"><label for="cMsg">Mensaje</label><textarea id="cMsg" name="mensaje" rows="4" required maxlength="2000" placeholder="Contanos en qué te podemos ayudar"></textarea></div>
        <label class="consent"><input type="checkbox" name="acepta_privacidad" value="si" required> <span>Acepto la <a href="/privacidad-y-terminos/" class="u">política de privacidad</a>.</span></label>
        <button type="submit" class="btn btn-pink btn-block">Enviar mensaje</button>
      </form>
    </div>
    <div>
      <div class="side-card">
        <div class="store-row" style="margin-bottom:16px;">%(iphone)s<div><b>WhatsApp</b><span><a href="%(wa)s" target="_blank" rel="noopener" data-wa class="u">%(tel)s</a></span></div></div>
        <div class="store-row" style="margin-bottom:16px;">%(imap)s<div><b>Local en Caballito</b><span>%(d1)s, CABA</span></div></div>
        <div class="store-row">%(iclock)s<div><b>Horarios</b><span>%(hor)s</span></div></div>
        %(email)s
      </div>
      <div class="side-card" style="background:var(--surface);border:1.5px solid var(--line);">
        <h2 style="font-size:16px;margin-bottom:4px;">Políticas</h2>
        <div class="policy-mini"><b>Envíos y medios de pago</b><a href="/envios-y-pagos/">Ver</a></div>
        <div class="policy-mini"><b>Cambios y devoluciones</b><a href="/cambios-y-devoluciones/">Ver</a></div>
        <div class="policy-mini"><b>Privacidad y términos</b><a href="/privacidad-y-terminos/">Ver</a></div>
      </div>
    </div>
  </div>
</section>''' % dict(ph=pagehead('¿Hablamos?', 'Consultas por talles, cambios, envíos o convenios institucionales: escribinos por el medio que prefieras.'),
                     iphone=ic('phone'), imap=ic('map'), iclock=ic('clock'), wa=wa_link(), tel=esc(N['telefonoVisible']),
                     d1=esc(N['direccion1']), hor=esc(N['horarios']), email=email_row)
    return page('/contacto/', 'Contacto y ubicación | %s' % NAME,
                'Escribinos por WhatsApp o desde el formulario. Local de calzado infantil en %s, Caballito. %s.' % (N['direccion1'], N['horarios'].split('·')[0].strip()),
                'contacto', body, ld=[local_business_ld()])


def policies():
    free = T.get('envioGratisDesde', 0)
    cost = T.get('costoEnvio', 0)
    if free and cost:
        ship = 'El envío es <b>gratuito</b> en compras superiores a %s; por debajo de ese monto tiene un costo fijo de %s.' % (money(free), money(cost))
    elif cost:
        ship = 'El envío tiene un costo fijo de %s.' % money(cost)
    else:
        ship = 'El envío es <b>gratuito</b>.'
    pays = ''.join('<li>%s</li>' % esc(x) for x in policy_pay_list())
    return {
        'envios-y-pagos': dict(
            title='Envíos y medios de pago | Funny Foot',
            desc='Cómo es el proceso de compra, envíos a todo el país, retiro en el local de Caballito y medios de pago de Funny Foot.',
            h1='Envíos y medios de pago',
            body='''<h2>Cómo es el proceso de compra</h2>
<p>Elegís los modelos y talles, completás tus datos, elegís envío o retiro y el medio de pago, y confirmás el pedido. Recibís un número de pedido y te contactamos por WhatsApp o email para confirmar disponibilidad, el total final y acordar el pago. Este sitio no cobra ni procesa pagos con tarjeta en línea.</p>
<h2>Envíos</h2>
<p>Realizamos envíos a todo el país a través de correo. %s %s</p>
<p>También podés retirar tu pedido sin cargo en nuestro local de %s, %s.</p>
<h2>Medios de pago</h2>
<ul>%s</ul>
<p>El medio de pago se confirma al coordinar el pedido con nosotros.</p>''' % (ship, esc(T.get('plazoEnvio', '')), esc(N['direccion1']), esc(N['direccion2']), pays)),
        'cambios-y-devoluciones': dict(
            title='Cambios y devoluciones | Funny Foot',
            desc='Política de cambios, devoluciones y botón de arrepentimiento de Funny Foot Calzados.',
            h1='Cambios y devoluciones',
            body='''<h2>¿Cómo cambio un producto?</h2>
<p>Tenés hasta <b>%d días corridos</b> desde la recepción para cambiar el talle o el modelo, siempre que el calzado esté sin uso y con su caja original. Podés iniciar el cambio escribiéndonos por WhatsApp o pasando directamente por el local de Caballito.</p>
<h2>Devoluciones</h2>
<p>Si el producto tiene una falla de fabricación, se reintegra el importe total o se cambia por otro modelo, a elección del cliente. Los costos de envío del cambio corren por cuenta de la tienda cuando la falla es de fabricación.</p>
<h2>Botón de arrepentimiento</h2>
<p>Conforme a la normativa de Defensa del Consumidor, disponés de 10 días corridos desde la compra para arrepentirte de la operación sin costo alguno. Para ejercer este derecho escribinos por WhatsApp o desde el <a href="/contacto/">formulario de contacto</a>.</p>''' % T.get('diasCambio', 30)),
        'privacidad-y-terminos': dict(
            title='Privacidad y términos de uso | Funny Foot',
            desc='Política de privacidad, uso de cookies y condiciones de uso del sitio de Funny Foot Calzados.',
            h1='Privacidad y términos de uso',
            body='''<h2>Responsable del sitio</h2>
<p>%(n)s, %(d1)s, %(d2)s. Contacto por WhatsApp al %(tel)s o desde el <a href="/contacto/">formulario de contacto</a>.</p>
<h2>Datos personales que recopilamos</h2>
<p>Los datos que nos compartís (nombre, email, teléfono, dirección de entrega, mensaje y los datos de tu pedido) se utilizan exclusivamente para gestionar tu compra, coordinar el envío, responder tus consultas y, si te suscribís, enviarte novedades. No compartimos tu información con terceros ajenos al proceso de venta y envío.</p>
<h2>Cómo se procesan</h2>
<p>Los formularios y pedidos del sitio se reciben a través de Netlify, el servicio donde está alojado. Las conversaciones por WhatsApp se procesan en esa aplicación, con sus propias condiciones. El sitio carga tipografías desde Google Fonts.</p>
<h2>Cookies y medición</h2>
<p>El carrito se guarda en tu propio navegador (almacenamiento local) para que no pierdas tu selección. Además, este sitio puede utilizar etiquetas de Google (Google Analytics y Google Ads) para medir las visitas y evaluar el resultado de nuestros anuncios. Esas etiquetas usan cookies e identificadores para recopilar datos de navegación de forma anónima o seudonimizada. Podés administrar los anuncios que ves desde la configuración de anuncios de tu cuenta de Google, o desactivar las cookies desde tu navegador.</p>
<h2>Tus derechos</h2>
<p>Podés pedirnos acceso, rectificación o eliminación de tus datos escribiéndonos por los medios de contacto indicados arriba. La Agencia de Acceso a la Información Pública, en su carácter de Órgano de Control de la Ley N° 25.326, tiene la atribución de atender las denuncias y reclamos que interpongan quienes resulten afectados en sus derechos por incumplimiento de las normas vigentes en materia de protección de datos personales.</p>
<h2>Condiciones de uso</h2>
<p>Los precios y la disponibilidad de talles pueden variar sin previo aviso y se confirman al recibir el pedido. Las imágenes son ilustraciones o fotos del modelo y color; pueden existir variaciones respecto del producto real. Los nombres de marcas y personajes pertenecen a sus respectivos titulares.</p>
<h2>Pagos</h2>
<p>Este sitio no procesa pagos con tarjeta en línea. El pago se acuerda con nosotros al confirmar tu pedido.</p>''' % dict(
                n=esc(NAME), d1=esc(N['direccion1']), d2=esc(N['direccion2']), tel=esc(N['telefonoVisible']))),
    }


def pg_policy(slug, p):
    body = '''%s
<section class="wrap"><div class="policy-body policy-page">%s</div></section>''' % (pagehead(p['h1'], '', [('Inicio', '/'), (p['h1'], None)]), p['body'])
    return page('/%s/' % slug, p['title'], p['desc'], '', body, with_feedback=False)


def pg_thanks(slug, h1, msg, conv):
    body = '''<section class="wrap thanks">
  <div class="success-box">
    <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.6 2.6L16 9.6"/></svg>
    <h1>%s</h1>
    <p>%s</p>
    <a href="/" class="btn btn-primary" style="margin-top:18px;">Volver al inicio</a>
  </div>
</section>''' % (esc(h1), esc(msg))
    return page('/%s/' % slug, h1 + ' | Funny Foot', msg, '', body, robots='noindex,follow',
                body_attr=(' data-conversion="lead"' if conv else ''), with_feedback=False)


PROVINCIAS = ['Ciudad Autónoma de Buenos Aires', 'Buenos Aires', 'Catamarca', 'Chaco', 'Chubut', 'Córdoba', 'Corrientes', 'Entre Ríos',
              'Formosa', 'Jujuy', 'La Pampa', 'La Rioja', 'Mendoza', 'Misiones', 'Neuquén', 'Río Negro', 'Salta', 'San Juan', 'San Luis',
              'Santa Cruz', 'Santa Fe', 'Santiago del Estero', 'Tierra del Fuego', 'Tucumán']


def pg_checkout():
    pay = ''
    for i, (val, label, desc, solo_retiro) in enumerate(payment_options()):
        pay += '''<label class="pay-option" data-pay="%s"%s><input type="radio" name="pago" value="%s"%s><span><b>%s</b><span>%s</span></span></label>
''' % (val, ' data-solo-retiro="1"' if solo_retiro else '', val, ' checked' if i == 0 else '', esc(label), esc(desc))
    provs = ''.join('<option value="%s"%s>%s</option>' % (esc(p), ' selected' if p.startswith('Ciudad') else '', esc(p)) for p in PROVINCIAS)
    body = '''%(ph)s
<section class="wrap">
  <div class="co-empty" id="coEmpty" hidden>
    <h2>Tu carrito está vacío</h2>
    <p>Elegí tus productos y volvé para finalizar la compra.</p>
    <a class="btn btn-pink" href="/productos/">Ver catálogo</a>
  </div>
  <div class="co-grid" id="coGrid">
    <form id="checkoutForm" class="co-form" name="pedido" method="POST" action="/pedido-recibido/" data-netlify="true" netlify-honeypot="bot-field" novalidate>
      <input type="hidden" name="form-name" value="pedido">
      <p class="hp" aria-hidden="true"><label>No completar este campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      <input type="hidden" name="pedido_numero" id="fNumero">
      <input type="hidden" name="productos" id="fProductos">
      <input type="hidden" name="productos_json" id="fProductosJson">
      <input type="hidden" name="subtotal" id="fSubtotal">
      <input type="hidden" name="descuento" id="fDescuento">
      <input type="hidden" name="envio" id="fEnvio">
      <input type="hidden" name="total" id="fTotal">

      <fieldset class="co-block">
        <legend>1. Tus datos</legend>
        <div class="field"><label for="fNombre">Nombre y apellido</label><input id="fNombre" name="nombre" autocomplete="name" maxlength="80" required><p class="err" data-err="nombre" hidden></p></div>
        <div class="field-row">
          <div class="field"><label for="fEmail">Email</label><input id="fEmail" name="email" type="email" autocomplete="email" maxlength="120" required><p class="err" data-err="email" hidden></p></div>
          <div class="field"><label for="fTel">Teléfono / WhatsApp</label><input id="fTel" name="telefono" type="tel" autocomplete="tel" maxlength="30" placeholder="11 0000-0000" required><p class="err" data-err="telefono" hidden></p></div>
        </div>
      </fieldset>

      <fieldset class="co-block">
        <legend>2. Entrega</legend>
        <label class="pay-option"><input type="radio" name="entrega" value="domicilio" checked><span><b>Envío a domicilio</b><span id="entregaDomDesc"></span></span></label>
        <label class="pay-option"><input type="radio" name="entrega" value="retiro"><span><b>Retiro en el local</b><span>Sin cargo · %(d1)s, %(d2)s</span></span></label>
        <div id="domBlock">
          <div class="field"><label for="fDir">Calle y número</label><input id="fDir" name="direccion" autocomplete="street-address" maxlength="120"><p class="err" data-err="direccion" hidden></p></div>
          <div class="field-row">
            <div class="field"><label for="fPiso">Piso / depto (opcional)</label><input id="fPiso" name="piso" maxlength="30"></div>
            <div class="field"><label for="fCP">Código postal</label><input id="fCP" name="cp" autocomplete="postal-code" maxlength="10" inputmode="text"><p class="err" data-err="cp" hidden></p></div>
          </div>
          <div class="field-row">
            <div class="field"><label for="fLoc">Localidad</label><input id="fLoc" name="localidad" autocomplete="address-level2" maxlength="80"><p class="err" data-err="localidad" hidden></p></div>
            <div class="field"><label for="fProv">Provincia</label><select id="fProv" name="provincia" autocomplete="address-level1">%(provs)s</select></div>
          </div>
        </div>
      </fieldset>

      <fieldset class="co-block">
        <legend>3. Medio de pago</legend>
%(pay)s        <p class="err" data-err="pago" hidden></p>
        <p class="note-small">No se te cobra en este sitio. Al confirmar, te contactamos para acordar el pago.</p>
      </fieldset>

      <fieldset class="co-block">
        <legend>4. Confirmar</legend>
        <div class="field"><label for="fNotas">Notas para el pedido (opcional)</label><textarea id="fNotas" name="notas" rows="3" maxlength="500" placeholder="Horarios de entrega, referencias, consultas…"></textarea></div>
        <label class="consent"><input type="checkbox" name="acepta" id="fAcepta" value="si" required> <span>Acepto los <a href="/privacidad-y-terminos/" class="u" target="_blank" rel="noopener">términos y la política de privacidad</a>.</span></label>
        <p class="err" data-err="acepta" hidden></p>
        <div class="co-alert" id="coAlert" role="alert" hidden></div>
        <button type="submit" class="btn btn-pink btn-block" id="coSubmit">Confirmar pedido</button>
      </fieldset>
    </form>

    <aside class="co-summary" aria-label="Resumen del pedido">
      <h2>Resumen del pedido</h2>
      <div id="coItems"></div>
      <div class="co-line"><span>Subtotal</span><span id="sSubtotal"></span></div>
      <div class="co-line" id="sDescRow" hidden><span id="sDescLabel">Descuento</span><span id="sDesc"></span></div>
      <div class="co-line"><span>Envío</span><span id="sEnvio"></span></div>
      <div class="co-line total"><span>Total</span><span id="sTotal"></span></div>
      <a class="u note-small" href="/productos/">← Seguir comprando</a>
    </aside>
  </div>
</section>''' % dict(ph=pagehead('Finalizar compra', 'Completá tus datos para confirmar el pedido.', [('Inicio', '/'), ('Finalizar compra', None)]),
                     d1=esc(N['direccion1']), d2=esc(N['direccion2']), provs=provs, pay=pay)
    return page('/checkout/', 'Finalizar compra | %s' % NAME, 'Completá tus datos para confirmar tu pedido en %s.' % NAME, '', body,
                robots='noindex,follow', with_feedback=False, extra_js='<script src="/assets/js/checkout.js" defer></script>\n')


def pg_recibido():
    body = '''%(ph)s
<section class="wrap">
  <div class="pedido-ok" id="pedidoOk" hidden>
    <div class="success-box">
      <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.6 2.6L16 9.6"/></svg>
      <h2 style="font-size:24px;">¡Recibimos tu pedido!</h2>
      <p>Guardá tu número de pedido:</p>
      <div class="order-num" id="oNumero"></div>
      <p id="oAviso"></p>
    </div>
    <div class="co-summary" style="max-width:640px;margin:0 auto;">
      <h2>Detalle</h2>
      <div id="oItems"></div>
      <div class="co-line"><span>Subtotal</span><span id="oSubtotal"></span></div>
      <div class="co-line" id="oDescRow" hidden><span>Descuento</span><span id="oDesc"></span></div>
      <div class="co-line"><span>Envío</span><span id="oEnvio"></span></div>
      <div class="co-line total"><span>Total a pagar</span><span id="oTotal"></span></div>
      <p class="note-small" id="oEntrega"></p>
    </div>
    <div class="co-next" id="oPago"></div>
    <div class="co-actions-row">
      <a class="btn btn-wa" id="oWa" href="%(wa)s" target="_blank" rel="noopener">Confirmar por WhatsApp</a>
      <a class="btn btn-outline" href="/productos/">Seguir comprando</a>
    </div>
  </div>
  <div class="co-empty" id="oVacio" hidden>
    <h2>No encontramos un pedido reciente</h2>
    <p>Si acabás de hacer un pedido y ves este mensaje, escribinos por WhatsApp con tu nombre y te ayudamos.</p>
    <a class="btn btn-pink" href="/productos/">Ver catálogo</a>
  </div>
</section>''' % dict(ph=pagehead('Pedido recibido', ''), wa=wa_link())
    return page('/pedido-recibido/', 'Pedido recibido | %s' % NAME, 'Recibimos tu pedido.', '', body, robots='noindex,follow',
                with_feedback=False, extra_js='<script src="/assets/js/checkout.js" defer></script>\n')


def pg_404():
    body = '''<section class="wrap thanks">
  <div class="success-box">
    <h1>No encontramos esa página</h1>
    <p>Puede que el enlace haya cambiado. Volvé al inicio o mirá el catálogo.</p>
    <div class="hero-cta" style="justify-content:center;"><a href="/" class="btn btn-primary">Ir al inicio</a><a href="/productos/" class="btn btn-pink">Ver catálogo</a></div>
  </div>
</section>'''
    return page('/404.html', 'Página no encontrada | Funny Foot', 'La página que buscás no existe.', '', body, robots='noindex,follow', with_feedback=False)


# ---------- salida ----------
def catalogo_js():
    cfg = {
        'nombre': NAME, 'whatsapp': N['whatsapp'], 'telefono': N['telefonoVisible'], 'direccion': '%s, %s' % (N['direccion1'], N['direccion2']),
        'horarios': N['horarios'],
        'envioGratisDesde': T.get('envioGratisDesde', 0), 'costoEnvio': T.get('costoEnvio', 0),
        'descuentoTransferencia': T.get('descuentoTransferencia', 0), 'datosTransferencia': T.get('datosTransferencia', ''),
        'metodosPago': [{'id': v, 'nombre': l, 'soloRetiro': s} for v, l, d, s in payment_options()],
    }
    prods = [{'id': p['id'], 'slug': p['slug'], 'nombre': p['nombre'], 'precio': p['precio'], 'talles': p['talles'],
              'imagen': p['imagenes'][0] if p['imagenes'] else '', 'color': p['color'], 'agotado': p['agotado']} for p in PRODUCTS]
    return '/* Generado por fuentes-del-sitio/build_site.py. No editar a mano: se pisa en cada publicación. */\nwindow.FF_CATALOGO = %s;\n' % json.dumps(
        {'config': cfg, 'productos': prods}, ensure_ascii=False, separators=(',', ':'))


def clean_generated():
    for d in ('producto', 'productos', 'gracias-sugerencia'):
        full = os.path.join(SITE, d)
        if os.path.isdir(full):
            shutil.rmtree(full)


def main():
    clean_generated()
    write('/', pg_home())
    write('/productos/', pg_productos())
    for c in CATS:
        write(c_url(c), pg_cat(c))
    for p in PRODUCTS:
        write(p_url(p), pg_product(p))
    write('/nosotros/', pg_nosotros())
    write('/preguntas-frecuentes/', pg_faq())
    write('/contacto/', pg_contacto())
    for slug, pol in policies().items():
        write('/%s/' % slug, pg_policy(slug, pol))
    write('/gracias/', pg_thanks('gracias', '¡Gracias por escribirnos!', 'Recibimos tu mensaje y te respondemos a la brevedad.', True))
    write('/gracias-suscripcion/', pg_thanks('gracias-suscripcion', '¡Ya estás en la lista!', 'Te vamos a avisar cuando haya novedades.', False))
    write('/checkout/', pg_checkout())
    write('/pedido-recibido/', pg_recibido())
    write('/404.html', pg_404())

    os.makedirs(os.path.join(SITE, 'assets', 'js'), exist_ok=True)
    with open(os.path.join(SITE, 'assets', 'js', 'catalogo.js'), 'w', encoding='utf-8') as fh:
        fh.write(catalogo_js())

    urls = ['/', '/productos/'] + [c_url(c) for c in CATS] + [p_url(p) for p in PRODUCTS] + \
           ['/nosotros/', '/preguntas-frecuentes/', '/contacto/', '/envios-y-pagos/', '/cambios-y-devoluciones/', '/privacidad-y-terminos/']
    prio = {'/': '1.0', '/productos/': '0.9'}
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>' % (BASE, u, TODAY, prio.get(u, '0.6')))
    sm.append('</urlset>')
    with open(os.path.join(SITE, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(sm) + '\n')
    with open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8') as fh:
        fh.write('User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: %s/sitemap.xml\n' % BASE)
    print('Sitio generado: %d productos, %d categorías, %d URLs en el sitemap' % (len(PRODUCTS), len(CATS), len(urls)))


if __name__ == '__main__':
    main()
