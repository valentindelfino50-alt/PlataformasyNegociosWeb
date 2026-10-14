#!/usr/bin/env python3
"""Genera el sitio estático de Funny Foot listo para Netlify."""
import html, json, os, shutil, sys
from PIL import Image

SCR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(SCR), 'funnyfoot-sitio')

# ---------------- datos del negocio (se reemplazan con reemplazar.js) ----------------
BASE = 'https://SU-SITIO.netlify.app'
NAME = 'Funny Foot Calzados'
ADDR1 = 'Av. Rivadavia 6521'
ADDR2 = 'Caballito, Ciudad de Buenos Aires'
HOURS = 'Lunes a viernes 10 a 19h · Sábados 10 a 14h'
PHONE = '11 5555-0199'
WA = '5491155550199'
TODAY = '2026-10-14'

CATS = [
    dict(key='led', slug='zapatillas-con-luz-led', label='Con luz LED', h1='Zapatillas con luz LED para niñas y niños',
         title='Zapatillas con luz LED para niños | Funny Foot',
         desc='Zapatillas con luz LED que se encienden al pisar, con personajes y colores para elegir. Talles {smin} al {smax}. Funny Foot, Caballito.',
         intro='Zapatillas con luces que se encienden al pisar, con personajes y colores para elegir. Elegí el talle y armá tu pedido.'),
    dict(key='botas', slug='botas-y-botitas', label='Botas y botitas FERLI', h1='Botas, borcegos y botitas FERLI',
         title='Botas y botitas FERLI para niñas | Funny Foot',
         desc='Botas, borcegos y botitas FERLI para niñas, en talles {smin} al {smax}. Elegí tu modelo y pedilo por WhatsApp. Funny Foot, Caballito.',
         intro='Botas, borcegos y pantubotas FERLI para el invierno, en varios talles y colores.'),
    dict(key='urbanas', slug='zapatillas-urbanas', label='Urbanas FERLI', h1='Zapatillas urbanas FERLI para el uso diario',
         title='Zapatillas urbanas FERLI para niñas | Funny Foot',
         desc='Zapatillas urbanas FERLI con cordón elastizado o cierre de abrojo, talles {smin} al {smax}. Pedilas por WhatsApp. Funny Foot, Caballito.',
         intro='Zapatillas FERLI pensadas para el uso de todos los días, con cordón elastizado o cierre de abrojo.'),
    dict(key='deportivas', slug='zapatillas-deportivas', label='Deportivas JAGUAR', h1='Zapatillas deportivas JAGUAR para chicos',
         title='Zapatillas deportivas JAGUAR para chicos | Funny Foot',
         desc='Zapatillas deportivas y urbanas JAGUAR para chicos, talles {smin} al {smax}. Elegí tu modelo y pedilo por WhatsApp. Funny Foot, Caballito.',
         intro='Zapatillas JAGUAR deportivas y urbanas para correr, jugar y usar todos los días.'),
]

PRODUCTS = [
    dict(id=1, name="Frozen FOOTY Corazón Lila con luz al pisar", cat='led', price=72900, sizeMin=23, sizeMax=28, color='#B57BDB', colorName='Lila', led=True),
    dict(id=2, name="Frozen FOOTY Together Celeste con luz al pisar", cat='led', price=72900, sizeMin=23, sizeMax=28, color='#5FA9DE', colorName='Celeste', led=True),
    dict(id=3, name="Stitch FOOTY Good Vibes Fucsia con luz al pisar", cat='led', price=72900, sizeMin=26, sizeMax=32, color='#ED0B6F', colorName='Fucsia', led=True),
    dict(id=4, name="Minnie FOOTY Star Lila con luz al pisar", cat='led', price=72900, sizeMin=22, sizeMax=26, color='#9C6BD9', colorName='Lila', led=True),
    dict(id=5, name="Zapatilla FOOTY Cars Race Rojo con luz al pisar", cat='led', price=72900, sizeMin=26, sizeMax=32, color='#E14336', colorName='Rojo', led=True),
    dict(id=6, name="Zapatilla POP FOOTY Mickey Azul Smiles con luz al pisar", cat='led', price=48000, sizeMin=22, sizeMax=26, color='#3E7FC1', colorName='Azul', led=True),
    dict(id=7, name="FOOTY Multi Star con luz al pisar", cat='led', price=74000, sizeMin=28, sizeMax=34, color='#E0A421', colorName='Dorado', led=True),
    dict(id=8, name="FORKI 04 Borcegos Nena Glitter Negro Charol FERLI", cat='botas', price=46000, sizeMin=23, sizeMax=28, color='#2E2A32', colorName='Negro', led=False),
    dict(id=9, name="GOBBY 07 Botitas Nena con Luces LED FERLI", cat='botas', price=46000, sizeMin=23, sizeMax=28, color='#A468C4', colorName='Lila', led=True),
    dict(id=10, name="Botita FERLI Benson", cat='botas', price=46000, sizeMin=23, sizeMax=28, color='#8C5A38', colorName='Marrón', led=False),
    dict(id=11, name="Pantubotas Nenas FERLI Piel abrigada", cat='botas', price=74000, sizeMin=29, sizeMax=34, color='#6E4A2E', colorName='Camel', led=False),
    dict(id=12, name="LENA 03 Zapatillas con luces LED niñas FERLI", cat='led', price=48000, sizeMin=23, sizeMax=28, color='#E0559A', colorName='Rosa', led=True),
    dict(id=13, name="MARILU 01 Zapatillas Nena Cordón Elastizado FERLI", cat='urbanas', price=59000, sizeMin=29, sizeMax=36, color='#E39AB6', colorName='Rosa pastel', led=False),
    dict(id=14, name="Zapatillas FERLI cierre de abrojo y elástico", cat='urbanas', price=59000, sizeMin=29, sizeMax=36, color='#9AA0A8', colorName='Gris', led=False),
    dict(id=15, name="Zapatillas JAGUAR Oficial Deportiva art. 4020", cat='deportivas', price=45000, sizeMin=30, sizeMax=35, color='#3E4E6B', colorName='Gris azulado', led=False),
    dict(id=16, name="Zapatillas JAGUAR Urbana Kids art. 4031", cat='deportivas', price=45000, sizeMin=27, sizeMax=33, color='#233047', colorName='Azul marino', led=False),
]
FEATURED = [1, 3, 5, 9, 12, 15]

esc = html.escape


def money(n):
    return '$' + f'{n:,}'.replace(',', '.')


def tint(hexc, amt):
    c = hexc.lstrip('#')
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return 'rgb(%d,%d,%d)' % (round(r + (255 - r) * amt), round(g + (255 - g) * amt), round(b + (255 - b) * amt))


def cat_range(key):
    ps = [p for p in PRODUCTS if p['cat'] == key]
    return min(p['sizeMin'] for p in ps), max(p['sizeMax'] for p in ps)


# ---------------- activos ----------------
def build_assets():
    os.makedirs(f'{OUT}/assets/css', exist_ok=True)
    os.makedirs(f'{OUT}/assets/js', exist_ok=True)
    os.makedirs(f'{OUT}/assets/img', exist_ok=True)
    ex = f'{SCR}/extract'
    shutil.copy(f'{ex}/8f586751.png', f'{OUT}/assets/img/logo-funny-foot-rosa.png')
    shutil.copy(f'{ex}/3f9fe507.png', f'{OUT}/assets/img/logo-funny-foot-blanco.png')
    shutil.copy(f'{ex}/de14d01a.png', f'{OUT}/assets/img/logo-funny-foot-fondo-rosa.png')
    # favicon y og-image a partir del logo con fondo rosa
    src = Image.open(f'{ex}/de14d01a.png').convert('RGB')
    bg = src.getpixel((4, 4))
    shoe = src.crop((14, 44, 246, 176))
    side = 232
    canvas = Image.new('RGB', (side, side), bg)
    canvas.paste(shoe, (0, (side - shoe.height) // 2))
    for size, rel in ((32, 'favicon-32.png'), (180, 'apple-touch-icon.png'), (192, 'assets/img/icon-192.png'), (512, 'assets/img/icon-512.png')):
        canvas.resize((size, size), Image.LANCZOS).save(f'{OUT}/{rel}')
    og = Image.new('RGB', (1200, 630), bg)
    logo = src.resize((960, 432), Image.LANCZOS)
    og.paste(logo, (120, 99))
    og.save(f'{OUT}/assets/img/og-funny-foot.png', optimize=True)
    # favicon svg
    with open(f'{OUT}/favicon.svg', 'w', encoding='utf-8') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="26" fill="#ED0B6F"/>'
                '<g transform="translate(6 20) scale(.95)" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">'
                '<line x1="2" y1="26" x2="16" y2="26"/><line x1="2" y1="34" x2="20" y2="34"/><line x1="2" y1="42" x2="14" y2="42"/>'
                '<path d="M28 46 C30 36 36 24 46 18 C50 24 58 27 66 27 L66 20 C74 20 84 24 92 32 C100 39 106 40 112 40 C114 48 112 58 104 62 L34 62 C28 62 26 54 28 46 Z"/>'
                '<path d="M34 62 L34 68 L112 68 L112 60"/></g></svg>')
    # web manifest
    with open(f'{OUT}/site.webmanifest', 'w', encoding='utf-8') as f:
        json.dump({
            'name': NAME, 'short_name': 'Funny Foot', 'lang': 'es-AR', 'start_url': '/', 'display': 'browser',
            'background_color': '#FFFCFD', 'theme_color': '#ED0B6F',
            'icons': [{'src': '/assets/img/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                      {'src': '/assets/img/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]
        }, f, ensure_ascii=False, indent=2)

    # CSS
    css = open(f'{SCR}/orig.css', encoding='utf-8').read()
    bad = ':root[data-theme="dark"] header.site, @media (prefers-color-scheme:dark){header.site{background:rgba(21,14,27,.86);}}'
    assert bad in css
    css = css.replace(bad, '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) header.site{background:rgba(21,14,27,.86);}}\n  :root[data-theme="dark"] header.site{background:rgba(21,14,27,.86);}')
    css += open(f'{SCR}/extra.css', encoding='utf-8').read()
    open(f'{OUT}/assets/css/estilos.css', 'w', encoding='utf-8').write(css)

    js = open(f'{SCR}/sitio.js', encoding='utf-8').read()
    slim = [dict(id=p['id'], name=p['name'], price=p['price']) for p in PRODUCTS]
    js = js.replace('__PRODUCTS__', json.dumps(slim, ensure_ascii=False))
    open(f'{OUT}/assets/js/sitio.js', 'w', encoding='utf-8').write(js)
    open(f'{OUT}/assets/js/config.js', 'w', encoding='utf-8').write(open(f'{SCR}/config.js', encoding='utf-8').read().replace('__WA__', WA))


SPRITE = open(f'{SCR}/sprite.svg.html', encoding='utf-8').read()

ICON_X = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><line x1="4" y1="4" x2="20" y2="20"/><line x1="20" y1="4" x2="4" y2="20"/></svg>'
ICON_PLUS = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>'
ICON_CART = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="21" r="1.4"/><circle cx="18" cy="21" r="1.4"/><path d="M2.5 3h2.4l2.6 12.4a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 2-1.6L21 7H6.2"/></svg>'
ICON_BURGER = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>'
ICON_WA = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 20l1.3-4A8 8 0 1 1 9 19l-5 1Z"/><path d="M8.5 9.7c0 3.4 2.8 6.2 6.2 6.2"/></svg>'


def ic(name, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true"><use href="#ic-{name}"/></svg>'


# ---------------- plantilla ----------------
def shopstore_ld():
    return {
        '@context': 'https://schema.org', '@type': 'ShoeStore', 'name': NAME, 'url': BASE + '/',
        'logo': BASE + '/assets/img/logo-funny-foot-rosa.png', 'image': BASE + '/assets/img/og-funny-foot.png',
        'telephone': '+54 9 11 5555-0199',
        'address': {'@type': 'PostalAddress', 'streetAddress': ADDR1, 'addressLocality': 'Caballito',
                    'addressRegion': 'Ciudad Autónoma de Buenos Aires', 'addressCountry': 'AR'},
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'opens': '10:00', 'closes': '19:00'},
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': 'Saturday', 'opens': '10:00', 'closes': '14:00'}],
    }


def head(title, desc, path, robots='index,follow,max-image-preview:large', ld=None):
    url = BASE + path
    ld_html = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in (ld or []))
    return f'''<!doctype html>
<html lang="es-AR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#ED0B6F">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_AR">
<meta property="og:site_name" content="{esc(NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/og-funny-foot.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/estilos.css">
{ld_html}</head>
'''


def header(active):
    items = [('inicio', '/', 'Inicio'), ('productos', '/productos/', 'Productos'), ('nosotros', '/nosotros/', 'Nosotros'), ('contacto', '/contacto/', 'Contacto')]
    def links(cls_extra=''):
        act = ' aria-current="page" class="active"'
        return ''.join('<a href="%s"%s>%s</a>' % (u, act if k == active else '', t) for k, u, t in items)
    return f'''<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="site">
  <div class="wrap bar">
    <a href="/" class="brandmark" aria-label="{esc(NAME)} - Inicio">
      <img src="/assets/img/logo-funny-foot-rosa.png" alt="{esc(NAME)}" width="76" height="34">
    </a>
    <nav class="primary" aria-label="Navegación principal">{links()}</nav>
    <div class="header-actions">
      <button type="button" class="icon-btn hamburger" id="hamburgerBtn" aria-label="Abrir menú" aria-expanded="false" aria-controls="mobileNav">{ICON_BURGER}</button>
      <button type="button" class="icon-btn" id="cartBtn" aria-label="Ver carrito">{ICON_CART}<span class="cart-count" id="cartCount" hidden>0</span></button>
    </div>
  </div>
</header>
<div id="mobileNav">{links()}</div>
'''


def feedback(path):
    return f'''
<section class="wrap fb" aria-labelledby="fbTitle">
  <div class="fb-card">
    <div class="fb-intro">
      <span class="kicker"><span class="dashline"><span></span><span></span><span></span></span>TU OPINIÓN NOS AYUDA</span>
      <h2 id="fbTitle">¿Qué agregarías, quitarías o cambiarías?</h2>
      <p>Contanos qué te gustó, qué te sobra y qué te falta en nuestra tienda. Leemos cada mensaje antes de decidir los próximos cambios.</p>
      <p>Tu comentario no se publica en la página.</p>
    </div>
    <form class="fb-form" name="sugerencias" method="POST" action="/gracias-sugerencia/" data-netlify="true" netlify-honeypot="bot-field">
      <input type="hidden" name="form-name" value="sugerencias">
      <input type="hidden" name="pagina" value="{esc(path)}">
      <p class="hp" aria-hidden="true"><label>No completar este campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      <fieldset class="fb-types">
        <legend>Mi comentario es para</legend>
        <label class="fb-opt"><input type="radio" name="tipo" value="agregar" checked><span>Agregar algo</span></label>
        <label class="fb-opt"><input type="radio" name="tipo" value="quitar"><span>Quitar algo</span></label>
        <label class="fb-opt"><input type="radio" name="tipo" value="cambiar"><span>Cambiar algo</span></label>
        <label class="fb-opt"><input type="radio" name="tipo" value="otro"><span>Otra idea</span></label>
      </fieldset>
      <div class="field">
        <label for="fbText">Tu mensaje</label>
        <textarea id="fbText" name="mensaje" rows="4" required minlength="5" maxlength="1000" placeholder="Por ejemplo: agregaría una guía de talles."></textarea>
      </div>
      <div class="field">
        <label for="fbName">Tu nombre (opcional)</label>
        <input id="fbName" name="nombre" maxlength="60" autocomplete="given-name">
      </div>
      <button type="submit" class="btn btn-pink btn-block">Enviar comentario</button>
    </form>
  </div>
</section>
'''


def footer():
    return f'''
<footer class="site">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <div class="brandmark"><img src="/assets/img/logo-funny-foot-blanco.png" alt="{esc(NAME)}" width="67" height="30" loading="lazy"></div>
        <p class="desc">Calzado infantil con estilo, calidad y mucha diversión. Local de barrio en Caballito, pedidos online para toda la Argentina.</p>
        <div class="social-row">
          <a href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Escribinos por WhatsApp" data-wa>{ICON_WA}</a>
        </div>
      </div>
      <div>
        <h4>TIENDA</h4>
        <ul>
          <li><a href="/productos/">Todos los productos</a></li>
          {''.join(f'<li><a href="/productos/{c["slug"]}/">{esc(c["label"])}</a></li>' for c in CATS)}
        </ul>
      </div>
      <div>
        <h4>AYUDA</h4>
        <ul>
          <li><a href="/contacto/">Contacto</a></li>
          <li><a href="/envios-y-pagos/">Envíos y pagos</a></li>
          <li><a href="/cambios-y-devoluciones/">Cambios y devoluciones</a></li>
          <li><a href="/privacidad-y-terminos/">Privacidad y términos</a></li>
        </ul>
      </div>
      <div>
        <h4>VISITANOS</h4>
        <ul>
          <li><a href="/nosotros/">{esc(ADDR1)}, {esc(ADDR2)}</a></li>
          <li><a href="/nosotros/">{esc(HOURS)}</a></li>
          <li><a href="https://wa.me/{WA}" target="_blank" rel="noopener" data-wa>WhatsApp {esc(PHONE)}</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 {esc(NAME)}. Todos los derechos reservados.</span>
      <span>Sitio desarrollado como parte de un trabajo práctico — Plataformas y Negocios Web</span>
    </div>
  </div>
</footer>

<div id="toast" role="status" aria-live="polite"><span class="dot"></span><span id="toastMsg">¡Agregado al carrito!</span></div>

<div class="overlay" id="overlay"></div>
<aside class="drawer" id="cartDrawer" aria-label="Carrito de compras" aria-hidden="true">
  <div class="drawer-head">
    <h2>Tu pedido</h2>
    <button type="button" class="modal-close" id="closeDrawer" aria-label="Cerrar carrito">{ICON_X}</button>
  </div>
  <div class="drawer-body" id="drawerBody"></div>
  <div class="drawer-foot" id="drawerFoot"></div>
</aside>

{SPRITE}
<script src="/assets/js/config.js"></script>
<script src="/assets/js/sitio.js" defer></script>
</body>
</html>
'''


def page(path, title, desc, active, body, robots='index,follow,max-image-preview:large', ld=None, body_attr='', with_feedback=True):
    out = head(title, desc, path, robots, ld) + header(active)
    out = out.replace('<body>', f'<body{body_attr}>', 1)
    out += '<main id="contenido">\n' + body + '\n</main>\n'
    if with_feedback:
        out += feedback(path)
    out += footer()
    return out


def write(path, content):
    d = os.path.join(OUT, path.strip('/'))
    if path.endswith('.html'):
        full = os.path.join(OUT, path.lstrip('/'))
    else:
        os.makedirs(d, exist_ok=True)
        full = os.path.join(d, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)


# ---------------- componentes ----------------
def card(p, h='h3'):
    sizes = ''.join(f'<option value="{s}">Talle {s}</option>' for s in range(p['sizeMin'], p['sizeMax'] + 1))
    led = f'<span class="led-chip"><svg width="9" height="9" viewBox="0 0 24 24" aria-hidden="true"><use href="#ic-spark"/></svg>LED</span>' if p['led'] else ''
    return f'''<article class="card-product" data-id="{p['id']}" data-name="{esc(p['name'].lower())}">
  <div class="card-media" style="background:{tint(p['color'], .82)}">{led}<svg style="color:{p['color']}" role="img" aria-label="Ilustración de zapatilla color {esc(p['colorName'].lower())}"><use href="#ic-sneaker"/></svg></div>
  <{h}>{esc(p['name'])}</{h}>
  <div class="card-meta"><span>{esc(p['colorName'])} · Talles {p['sizeMin']}–{p['sizeMax']}</span></div>
  <div class="price">{money(p['price'])}</div>
  <div class="card-foot">
    <label class="sr-only" for="size-{p['id']}">Talle de {esc(p['name'])}</label>
    <select class="size-select" id="size-{p['id']}"><option value="">Talle</option>{sizes}</select>
    <button type="button" class="add-btn" data-add="{p['id']}" aria-label="Agregar {esc(p['name'])} al carrito">{ICON_PLUS}</button>
  </div>
</article>'''


def pagehead(h1, intro, crumbs=None):
    cr = ''
    if crumbs:
        parts = []
        for i, (label, url) in enumerate(crumbs):
            parts.append(f'<a href="{url}">{esc(label)}</a>' if url else f'<span aria-current="page">{esc(label)}</span>')
        cr = '<nav class="crumbs" aria-label="Migas de pan">' + ' <span aria-hidden="true">›</span> '.join(parts) + '</nav>'
    return f'''<div class="wrap">
  <div class="page-head">
    {cr}
    <div class="dashline" style="margin-bottom:16px;"><span></span><span></span><span></span></div>
    <h1>{esc(h1)}</h1>
    <p>{esc(intro)}</p>
  </div>
</div>'''


def listing(active_key):
    chips = '<a class="chip-filter%s" href="/productos/">Todas</a>' % (' active' if active_key is None else '')
    for c in CATS:
        chips += '<a class="chip-filter%s" href="/productos/%s/">%s</a>' % (' active' if c['key'] == active_key else '', c['slug'], esc(c['label']))
    ps = [p for p in PRODUCTS if active_key is None or p['cat'] == active_key]
    return f'''<div class="wrap">
  <div class="filter-bar" id="filterBar">{chips}
    <label class="sr-only" for="searchInput">Buscar por nombre</label>
    <input type="search" class="search-input" id="searchInput" placeholder="Buscar por nombre...">
  </div>
  <div class="grid-products" id="productsGrid">
{chr(10).join(card(p, 'h2') for p in ps)}
  </div>
  <div class="empty-state" id="emptyState" hidden>No encontramos productos con esa búsqueda. Probá con otra palabra o categoría.</div>
  <p class="note-small">Las imágenes son ilustraciones del modelo y color. Los precios y la disponibilidad de talles pueden variar; los confirmamos al recibir tu pedido por WhatsApp.</p>
</div>'''


# ---------------- páginas ----------------
def pg_home():
    feat = [p for p in PRODUCTS if p['id'] in FEATURED]
    cats = ''.join(
        f'<a class="cat-chip" href="/productos/{c["slug"]}/">{ic(i)}<b>{esc(c["label"])}</b><span>{esc(s)}</span></a>'
        for c, i, s in zip(CATS, ('spark', 'shield', 'heart', 'star'),
                           ('Personajes favoritos, se iluminan al pisar', 'Abrigo y resistencia para el invierno', 'Para el uso de todos los días', 'Comodidad para correr y jugar')))
    body = f'''<section class="hero">
  <div class="hero-panel"></div>
  <div class="wrap hero-inner">
    <div class="hero-copy">
      <span class="kicker"><span class="dashline"><span></span><span></span><span></span></span>TIENDA FAMILIAR EN CABALLITO</span>
      <h1>Zapatillas que iluminan cada paso</h1>
      <p>Calzado infantil con estilo, comodidad y mucha diversión: personajes con luz LED, botas FERLI y deportivas JAGUAR. Del local de barrio a tu casa, en todo el país.</p>
      <div class="hero-cta">
        <a href="/productos/" class="btn btn-pink">Ver catálogo</a>
        <a href="/nosotros/" class="btn btn-outline-light">Visitanos en Caballito</a>
      </div>
    </div>
    <div class="hero-visual">
      <div class="hero-badge">
        <img src="/assets/img/logo-funny-foot-blanco.png" alt="{esc(NAME)}" width="238" height="107">
        <div class="spark-row"><span class="dot"></span> Zapatillas con luz LED al pisar</div>
      </div>
    </div>
  </div>
</section>

<section class="wrap">
  <div class="section-head"><h2>Elegí por categoría</h2></div>
  <div class="cat-row">{cats}</div>
</section>

<section class="wrap">
  <div class="section-head">
    <div><h2>Destacados</h2><p>Algunos de los modelos que tenemos disponibles.</p></div>
    <a href="/productos/" class="btn btn-outline btn-sm">Ver todo</a>
  </div>
  <div class="grid-products">
{chr(10).join(card(p) for p in feat)}
  </div>
</section>

<section class="wrap">
  <div class="section-head"><h2>Cómo comprar</h2></div>
  <ol class="steps-list">
    <li><b>Elegí modelo y talle</b><span>Recorré el catálogo y sumá al pedido lo que te guste.</span></li>
    <li><b>Enviá tu pedido por WhatsApp</b><span>Con un toque armamos el mensaje con tu selección.</span></li>
    <li><b>Coordinamos pago y entrega</b><span>Te confirmamos disponibilidad y acordamos envío o retiro en el local.</span></li>
  </ol>
</section>

<section class="wrap">
  <div class="section-head"><h2>Por qué elegirnos</h2></div>
  <div class="props-grid">
    <div class="prop">{ic('shield')}<h3>Calidad que dura</h3><p>Materiales resistentes pensados para el ritmo de los más chicos.</p></div>
    <div class="prop">{ic('heart')}<h3>Comodidad de verdad</h3><p>Modelos pensados para usar todo el día.</p></div>
    <div class="prop">{ic('users')}<h3>Atención de barrio</h3><p>Te asesoramos como en el local de toda la vida, ahora también online.</p></div>
    <div class="prop">{ic('truck')}<h3>Envíos a todo el país</h3><p>Recibilo en tu casa o retiralo sin cargo en nuestro local de Caballito.</p></div>
  </div>
</section>

<section class="wrap">
  <div class="section-head"><h2>Nuestro local</h2></div>
  <div class="store-card">
    <div class="store-info">
      <div class="store-row">{ic('map')}<div><b>{esc(ADDR1)}</b><span>{esc(ADDR2)}</span></div></div>
      <div class="store-row">{ic('clock')}<div><b>Horarios</b><span>{esc(HOURS)}</span></div></div>
      <div class="store-row">{ic('phone')}<div><b>WhatsApp</b><span>{esc(PHONE)}</span></div></div>
      <a href="/nosotros/" class="btn btn-primary btn-sm" style="width:fit-content;">Conocer la tienda</a>
    </div>
    <div class="store-map"><svg width="120" height="120" viewBox="0 0 24 24" style="color:var(--pink)" aria-hidden="true"><use href="#ic-map"/></svg></div>
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
</section>'''
    return page('/', 'Funny Foot | Zapatillas y calzado infantil en Caballito',
                'Zapatillas con luz LED, botas FERLI y deportivas JAGUAR para niñas y niños. Local en Caballito, pedidos online para todo el país.',
                'inicio', body, ld=[shopstore_ld()])


def pg_productos():
    body = pagehead('Todo nuestro calzado', 'Zapatillas con luz LED, botas y botitas FERLI, urbanas y deportivas JAGUAR. Elegí talle y sumalo a tu pedido.',
                    [('Inicio', '/'), ('Productos', None)]) + '\n' + listing(None)
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Productos', 'item': BASE + '/productos/'}]}]
    return page('/productos/', 'Calzado infantil: zapatillas, botas y deportivas | Funny Foot',
                'Catálogo de calzado infantil: zapatillas con luz LED, botas y botitas FERLI, urbanas y deportivas JAGUAR. Pedí por WhatsApp.',
                'productos', body, ld=ld)


def pg_cat(c):
    smin, smax = cat_range(c['key'])
    body = pagehead(c['h1'], c['intro'], [('Inicio', '/'), ('Productos', '/productos/'), (c['label'], None)]) + '\n' + listing(c['key'])
    ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Productos', 'item': BASE + '/productos/'},
        {'@type': 'ListItem', 'position': 3, 'name': c['label'], 'item': f'{BASE}/productos/{c["slug"]}/'}]}]
    return page(f'/productos/{c["slug"]}/', c['title'], c['desc'].format(smin=smin, smax=smax), 'productos', body, ld=ld)


def pg_nosotros():
    body = f'''{pagehead('De un local de Caballito a tu casa', 'Conocé quiénes somos y dónde encontrarnos.')}
<section class="wrap">
  <div class="about-grid">
    <div class="about-copy">
      <p>Funny Foot nació como un local de barrio en Caballito y hoy también vive en internet. Somos una empresa familiar dedicada a vestir los pies de niñas y niños con calzado cómodo, resistente y con mucha onda.</p>
      <p>Desde las clásicas zapatillas urbanas hasta los modelos con luces LED que son furor entre los más chicos, elegimos cada modelo pensando en el uso diario: que aguanten el recreo, la plaza y el fin de semana.</p>
      <p>Seguimos atendiendo como el primer día: con nombre y apellido, aconsejando el talle justo y resolviendo cualquier cambio sin vueltas.</p>
      <a href="/productos/" class="btn btn-pink">Ver catálogo</a>
    </div>
    <div class="plaque"><img src="/assets/img/logo-funny-foot-fondo-rosa.png" alt="Logo de {esc(NAME)}" width="640" height="288" loading="lazy"></div>
  </div>
</section>
<section class="wrap">
  <div class="section-head"><h2>Lo que nos representa</h2></div>
  <div class="values-grid">
    <div class="value-card">{ic('users')}<h3>Cercanía</h3><p>Trato de barrio, tanto en el local como por WhatsApp.</p></div>
    <div class="value-card">{ic('shield')}<h3>Calidad</h3><p>Seleccionamos marcas que resisten el uso diario de los chicos.</p></div>
    <div class="value-card">{ic('spark')}<h3>Diversión</h3><p>Personajes y luces que hacen del calzado algo especial.</p></div>
    <div class="value-card">{ic('heart')}<h3>Comunidad</h3><p>Convenios con colegios de la zona y clientas de toda la vida.</p></div>
  </div>
  <div class="callout">
    {ic('map')}
    <p><b>¿Sabías que</b> trabajamos junto a colegios de Caballito para equipar a los chicos con calzado escolar y deportivo al inicio de cada ciclo lectivo? Consultanos por convenios institucionales.</p>
  </div>
</section>
<section class="wrap">
  <div class="section-head"><h2>Visitá nuestro local</h2></div>
  <div class="store-card">
    <div class="store-info">
      <div class="store-row">{ic('map')}<div><b>{esc(ADDR1)}</b><span>{esc(ADDR2)}</span></div></div>
      <div class="store-row">{ic('clock')}<div><b>Horarios</b><span>{esc(HOURS)}</span></div></div>
      <div class="store-row">{ic('truck')}<div><b>Retiro en local</b><span>Sin cargo, al coordinar tu pedido por WhatsApp</span></div></div>
      <a href="/contacto/" class="btn btn-primary btn-sm" style="width:fit-content;">Escribinos</a>
    </div>
    <div class="store-map"><svg width="120" height="120" viewBox="0 0 24 24" style="color:var(--pink)" aria-hidden="true"><use href="#ic-map"/></svg></div>
  </div>
</section>'''
    return page('/nosotros/', 'Nosotros | Funny Foot, local de calzado en Caballito',
                'Funny Foot es un local familiar de calzado infantil en Caballito, Buenos Aires. Conocé nuestra historia, horarios y cómo llegar.',
                'nosotros', body, ld=[shopstore_ld()])


def pg_contacto():
    body = f'''{pagehead('¿Hablamos?', 'Consultas por talles, cambios, envíos o convenios institucionales: escribinos por el medio que prefieras.')}
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
        <div class="store-row" style="margin-bottom:16px;">{ic('phone')}<div><b>WhatsApp</b><span><a href="https://wa.me/{WA}" target="_blank" rel="noopener" data-wa class="u">{esc(PHONE)}</a></span></div></div>
        <div class="store-row" style="margin-bottom:16px;">{ic('map')}<div><b>Local en Caballito</b><span>{esc(ADDR1)}, CABA</span></div></div>
        <div class="store-row">{ic('clock')}<div><b>Horarios</b><span>{esc(HOURS)}</span></div></div>
      </div>
      <div class="side-card" style="background:var(--surface);border:1.5px solid var(--line);">
        <h2 style="font-size:16px;margin-bottom:4px;">Políticas</h2>
        <div class="policy-mini"><b>Envíos y medios de pago</b><a href="/envios-y-pagos/">Ver</a></div>
        <div class="policy-mini"><b>Cambios y devoluciones</b><a href="/cambios-y-devoluciones/">Ver</a></div>
        <div class="policy-mini"><b>Privacidad y términos</b><a href="/privacidad-y-terminos/">Ver</a></div>
      </div>
    </div>
  </div>
</section>'''
    return page('/contacto/', 'Contacto y ubicación | Funny Foot Calzados',
                'Escribinos por WhatsApp o desde el formulario. Local de calzado infantil en Av. Rivadavia 6521, Caballito. Lunes a viernes 10 a 19h.',
                'contacto', body, ld=[shopstore_ld()])


POLICY = {
    'envios-y-pagos': dict(
        title='Envíos y medios de pago | Funny Foot',
        desc='Cómo coordinamos pedidos, envíos a todo el país, retiro en el local de Caballito y medios de pago de Funny Foot.',
        h1='Envíos y medios de pago',
        body='''<h2>Cómo hacés tu pedido</h2>
<p>Elegís los modelos y talles en el sitio y enviás el pedido por WhatsApp. Te confirmamos disponibilidad, precio final y forma de entrega. Este sitio no cobra ni procesa pagos en línea.</p>
<h2>Envíos</h2>
<p>Realizamos envíos a todo el país a través de correo. El envío es <b>gratuito</b> en compras superiores a $50.000; por debajo de ese monto tiene un costo fijo de $4.500. El tiempo estimado de entrega es de 2 a 5 días hábiles en CABA y GBA, y de 4 a 8 días hábiles en el resto del país.</p>
<p>También podés retirar tu pedido sin cargo en nuestro local de Av. Rivadavia 6521, Caballito, dentro de las 24 hs de confirmada la compra.</p>
<h2>Medios de pago</h2>
<ul>
  <li>Tarjetas de crédito y débito, hasta 3 cuotas sin interés</li>
  <li>Mercado Pago (QR o link de pago)</li>
  <li>Transferencia bancaria, con 5% de descuento</li>
  <li>Efectivo en el local de Caballito</li>
</ul>
<p>El medio de pago se acuerda al confirmar el pedido por WhatsApp.</p>'''),
    'cambios-y-devoluciones': dict(
        title='Cambios y devoluciones | Funny Foot',
        desc='Política de cambios, devoluciones y botón de arrepentimiento de Funny Foot Calzados.',
        h1='Cambios y devoluciones',
        body='''<h2>¿Cómo cambio un producto?</h2>
<p>Tenés hasta <b>30 días corridos</b> desde la recepción para cambiar el talle o el modelo, siempre que el calzado esté sin uso y con su caja original. Podés iniciar el cambio escribiéndonos por WhatsApp o pasando directamente por el local de Caballito.</p>
<h2>Devoluciones</h2>
<p>Si el producto tiene una falla de fabricación, se reintegra el importe total o se cambia por otro modelo, a elección del cliente. Los costos de envío del cambio corren por cuenta de la tienda cuando la falla es de fabricación.</p>
<h2>Botón de arrepentimiento</h2>
<p>Conforme a la normativa de Defensa del Consumidor, disponés de 10 días corridos desde la compra para arrepentirte de la operación sin costo alguno. Para ejercer este derecho escribinos por WhatsApp o desde el <a href="/contacto/">formulario de contacto</a>.</p>'''),
    'privacidad-y-terminos': dict(
        title='Privacidad y términos de uso | Funny Foot',
        desc='Política de privacidad, uso de cookies y condiciones de uso del sitio de Funny Foot Calzados.',
        h1='Privacidad y términos de uso',
        body=f'''<h2>Responsable del sitio</h2>
<p>{esc(NAME)}, {esc(ADDR1)}, {esc(ADDR2)}. Contacto por WhatsApp al {esc(PHONE)} o desde el <a href="/contacto/">formulario de contacto</a>.</p>
<h2>Datos personales que recopilamos</h2>
<p>Los datos que nos compartís (nombre, email, teléfono, mensaje y los datos de tu pedido) se utilizan exclusivamente para gestionar tu compra, coordinar el envío, responder tus consultas y, si te suscribís, enviarte novedades. No compartimos tu información con terceros ajenos al proceso de venta y envío.</p>
<h2>Cómo se procesan</h2>
<p>Los formularios del sitio se reciben a través de Netlify, el servicio donde está alojado. Los pedidos y consultas por WhatsApp se procesan en esa aplicación, con sus propias condiciones. El sitio carga tipografías desde Google Fonts.</p>
<h2>Cookies y medición</h2>
<p>El carrito se guarda en tu propio navegador (almacenamiento local) para que no pierdas tu selección. Además, este sitio puede utilizar etiquetas de Google (Google Analytics y Google Ads) para medir las visitas y evaluar el resultado de nuestros anuncios. Esas etiquetas usan cookies e identificadores para recopilar datos de navegación de forma anónima o seudonimizada. Podés administrar los anuncios que ves desde la configuración de anuncios de tu cuenta de Google, o desactivar las cookies desde tu navegador.</p>
<h2>Tus derechos</h2>
<p>Podés pedirnos acceso, rectificación o eliminación de tus datos escribiéndonos por los medios de contacto indicados arriba. La Agencia de Acceso a la Información Pública, en su carácter de Órgano de Control de la Ley N° 25.326, tiene la atribución de atender las denuncias y reclamos que interpongan quienes resulten afectados en sus derechos por incumplimiento de las normas vigentes en materia de protección de datos personales.</p>
<h2>Condiciones de uso</h2>
<p>Los precios y la disponibilidad de talles pueden variar sin previo aviso y se confirman al recibir el pedido por WhatsApp. Las imágenes son ilustraciones del modelo y color; pueden existir variaciones respecto del producto real. Los nombres de marcas y personajes pertenecen a sus respectivos titulares.</p>
<h2>Pagos</h2>
<p>Este sitio no procesa pagos en línea. El pago se acuerda con nosotros al confirmar tu pedido.</p>'''),
}


def pg_policy(slug):
    p = POLICY[slug]
    body = f'''{pagehead(p['h1'], '', [('Inicio', '/'), (p['h1'], None)])}
<section class="wrap"><div class="policy-body policy-page">{p['body']}</div></section>'''
    return page(f'/{slug}/', p['title'], p['desc'], '', body, with_feedback=False)


def pg_thanks(slug, h1, msg, conv):
    body = f'''<section class="wrap thanks">
  <div class="success-box">
    <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.6 2.6L16 9.6"/></svg>
    <h1>{esc(h1)}</h1>
    <p>{esc(msg)}</p>
    <a href="/" class="btn btn-primary" style="margin-top:18px;">Volver al inicio</a>
  </div>
</section>'''
    return page(f'/{slug}/', h1 + ' | Funny Foot', msg, '', body, robots='noindex,follow', body_attr=(' data-conversion="lead"' if conv else ''), with_feedback=False)


def pg_404():
    body = f'''<section class="wrap thanks">
  <div class="success-box">
    <h1>No encontramos esa página</h1>
    <p>Puede que el enlace haya cambiado. Volvé al inicio o mirá el catálogo.</p>
    <div class="hero-cta" style="justify-content:center;"><a href="/" class="btn btn-primary">Ir al inicio</a><a href="/productos/" class="btn btn-pink">Ver catálogo</a></div>
  </div>
</section>'''
    return page('/404.html', 'Página no encontrada | Funny Foot', 'La página que buscás no existe.', '', body, robots='noindex,follow', with_feedback=False)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_assets()
    write('/', pg_home())
    write('/productos/', pg_productos())
    for c in CATS:
        write(f'/productos/{c["slug"]}/', pg_cat(c))
    write('/nosotros/', pg_nosotros())
    write('/contacto/', pg_contacto())
    for slug in POLICY:
        write(f'/{slug}/', pg_policy(slug))
    write('/gracias/', pg_thanks('gracias', '¡Gracias por escribirnos!', 'Recibimos tu mensaje y te respondemos a la brevedad.', True))
    write('/gracias-sugerencia/', pg_thanks('gracias-sugerencia', '¡Gracias por tu comentario!', 'Leemos cada sugerencia para mejorar la tienda.', False))
    write('/gracias-suscripcion/', pg_thanks('gracias-suscripcion', '¡Ya estás en la lista!', 'Te vamos a avisar cuando haya novedades.', False))
    write('/404.html', pg_404())

    urls = ['/', '/productos/'] + [f'/productos/{c["slug"]}/' for c in CATS] + ['/nosotros/', '/contacto/'] + [f'/{s}/' for s in POLICY]
    prio = {'/': '1.0', '/productos/': '0.9'}
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f'  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{prio.get(u, "0.6")}</priority></url>')
    sm.append('</urlset>')
    open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write('\n'.join(sm) + '\n')
    open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
    open(f'{OUT}/_headers', 'w', encoding='utf-8').write(
        '/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: SAMEORIGIN\n  Referrer-Policy: strict-origin-when-cross-origin\n'
        '/assets/*\n  Cache-Control: public, max-age=86400\n')
    print('ok', len(urls), 'paginas en sitemap')


if __name__ == '__main__':
    main()
