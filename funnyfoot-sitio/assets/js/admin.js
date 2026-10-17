/* Panel de administración de Funny Foot.
 *
 * Qué hace: edita datos/productos.json y sube fotos al sitio. Entra con usuario y código; el servidor
 * (netlify/functions/admin.js) valida el acceso y publica en GitHub con una clave que NO está en el sitio.
 * Netlify detecta el cambio, regenera las páginas con fuentes-del-sitio/build_site.py y publica el sitio.
 */
(function () {
  'use strict';

  var API = '/.netlify/functions/admin';
  var USUARIO = 'PlataformasyNegocios';
  var MAX_FOTOS = 6;
  var ICONOS = [['spark', 'Destello'], ['shield', 'Escudo'], ['heart', 'Corazón'], ['star', 'Estrella'], ['shirt', 'Prenda'], ['users', 'Personas']];
  var SNEAKER = '<svg viewBox="0 0 120 80" aria-hidden="true" style="color:%C"><g fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><line x1="2" y1="26" x2="16" y2="26"/><line x1="2" y1="34" x2="20" y2="34"/><path d="M28 46 C30 36 36 24 46 18 C50 24 58 27 66 27 L66 20 C74 20 84 24 92 32 C100 39 106 40 112 40 C114 48 112 58 104 62 L34 62 C28 62 26 54 28 46 Z"/><path d="M34 62 L34 68 L112 68 L112 60"/></g></svg>';

  var metaBase = document.querySelector('meta[name="ff-base"]');
  var BASE = metaBase ? metaBase.content : '/';

  function $(id) { return document.getElementById(id); }
  function h(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function money(n) { return '$' + Math.round(n || 0).toLocaleString('es-AR'); }
  function slugify(s) {
    s = String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    return s.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'item';
  }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function rand(n) {
    var c = 'abcdefghijklmnopqrstuvwxyz0123456789', r = '';
    for (var i = 0; i < n; i++) r += c.charAt(Math.floor(Math.random() * c.length));
    return r;
  }
  function store(kind) { try { return kind === 'local' ? window.localStorage : window.sessionStorage; } catch (e) { return null; } }
  function getItem(k) { var a = store('session'), b = store('local'); return (a && a.getItem(k)) || (b && b.getItem(k)) || ''; }

  var toastTimer;
  function toast(msg) {
    var t = $('toast'); if (!t) return;
    $('toastMsg').textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.classList.remove('show'); }, 3200);
  }

  /* ------------------------------------------------------------------ estado */
  var S = {
    mode: '',            // 'sitio' | 'demo'
    session: '',
    data: null,          // copia de trabajo
    orig: '',            // JSON normalizado tal como se cargó
    baseSha: '',         // sha de datos/productos.json en la rama
    pending: {},         // ruta -> { dataUrl, base64 }
    tab: 'productos',
    filter: { q: '', cat: '', estado: '' },
    editing: null,       // { kind:'prod'|'cat', isNew, draft, added:[] }
    publishing: false
  };

  /* ------------------------------------------------------------------ servidor */
  function sessionToken() { return getItem('ff_admin_sesion'); }
  function sessionValid(tok) {
    var m = /^([a-z0-9]+)\./.exec(tok || '');
    return !!m && parseInt(m[1], 36) > Date.now() + 60000;
  }
  async function api(action, body) {
    var headers = { 'Content-Type': 'application/json' };
    if (action !== 'login' && S.session) headers['Authorization'] = 'Bearer ' + S.session;
    var res;
    try { res = await fetch(API, { method: 'POST', headers: headers, body: JSON.stringify(Object.assign({ action: action }, body || {})) }); }
    catch (e) { var ne = new Error('red'); ne.network = true; throw ne; }
    var j = {};
    try { j = await res.json(); } catch (e) { j = {}; }
    if (!res.ok) { var err = new Error(j.message || ('HTTP ' + res.status)); err.status = res.status; err.code = j.error; throw err; }
    return j;
  }
  function explain(e) {
    if (e && e.network) return 'No se pudo conectar con el servidor. Revisá tu conexión e intentá de nuevo.';
    var s = e && e.status;
    if (s && !(e && e.code)) return 'El servicio de administración no está disponible en esta dirección. Funciona en el sitio publicado en Netlify; acá podés usar el modo demostración.';
    if (s === 401 && e.code === 'credenciales') return 'Usuario o código incorrectos.';
    if (s === 401) return 'La sesión venció. Volvé a entrar.';
    if (e && e.message && s) return e.message;
    return 'Ocurrió un error inesperado. Intentá de nuevo.';
  }

  async function publishViaApi(files, message, onStep) {
    var entries = [], jsonSha = '';
    for (var i = 0; i < files.length; i++) {
      var f = files[i];
      if (f.remove) { entries.push({ path: f.path, sha: null }); continue; }
      onStep('Subiendo ' + f.path.split('/').pop() + '… (' + (i + 1) + ' de ' + files.length + ')');
      var r = f.isData ? await api('blob', { kind: 'datos', text: f.text }) : await api('blob', { kind: 'foto', base64: f.base64 });
      if (f.isData) jsonSha = r.sha;
      entries.push({ path: f.path, sha: r.sha });
    }
    onStep('Creando la publicación…');
    var c = await api('commit', { entries: entries, message: message, baseSha: S.baseSha });
    return { sha: c.sha, url: c.url, jsonSha: c.jsonSha || jsonSha };
  }

  /* ------------------------------------------------------------------ datos */
  function normalize(d) {
    d.negocio = d.negocio || {}; d.tienda = d.tienda || {}; d.tienda.metodosPago = d.tienda.metodosPago || {};
    d.categorias = d.categorias || []; d.productos = d.productos || [];
    return d;
  }
  function byIdMap(arr) { var m = {}; arr.forEach(function (x) { m[x.id] = x; }); return m; }
  function refs(d) { var s = {}; d.productos.forEach(function (p) { (p.imagenes || []).forEach(function (i) { s[i] = true; }); }); return s; }
  function catName(id) { var c = S.data.categorias.filter(function (x) { return x.id === id; })[0]; return c ? c.nombre : '—'; }
  function imgSrc(path) { return S.pending[path] ? S.pending[path].dataUrl : (BASE + path); }
  function nextProductId() { return S.data.productos.reduce(function (m, p) { return Math.max(m, p.id); }, 0) + 1; }

  function parseTalles(text) {
    var out = {}, bad = false;
    String(text).split(/[,;\s]+/).filter(Boolean).forEach(function (tok) {
      var m = tok.match(/^(\d{1,2})\s*[-–a]\s*(\d{1,2})$/);
      if (m) { var a = +m[1], b = +m[2]; if (a > b) { var t = a; a = b; b = t; } if (b - a > 30) { bad = true; return; } for (var i = a; i <= b; i++) out[i] = true; }
      else if (/^\d{1,2}$/.test(tok)) out[+tok] = true; else bad = true;
    });
    var arr = Object.keys(out).map(Number).filter(function (n) { return n >= 14 && n <= 50; }).sort(function (a, b) { return a - b; });
    return { list: arr, bad: bad || !arr.length };
  }
  function formatTalles(arr) {
    if (!arr || !arr.length) return '';
    var parts = [], s = arr[0], p = arr[0];
    for (var i = 1; i <= arr.length; i++) {
      if (arr[i] === p + 1) { p = arr[i]; continue; }
      parts.push(s === p ? String(s) : s + '-' + p);
      s = p = arr[i];
    }
    return parts.join(', ');
  }

  function summary() {
    var orig = JSON.parse(S.orig), cur = S.data;
    var om = byIdMap(orig.productos), cm = byIdMap(cur.productos);
    var added = [], removed = [], changed = [];
    cur.productos.forEach(function (p) { if (!om[p.id]) added.push(p); else if (JSON.stringify(om[p.id]) !== JSON.stringify(p)) changed.push(p); });
    orig.productos.forEach(function (p) { if (!cm[p.id]) removed.push(p); });
    var now = refs(cur), before = refs(orig);
    var upload = Object.keys(S.pending).filter(function (k) { return now[k]; });
    var del = Object.keys(before).filter(function (k) { return !now[k] && k.indexOf('assets/productos/') === 0; });
    var cats = JSON.stringify(orig.categorias) !== JSON.stringify(cur.categorias);
    var biz = JSON.stringify(orig.negocio) !== JSON.stringify(cur.negocio) || JSON.stringify(orig.tienda) !== JSON.stringify(cur.tienda);
    var n = added.length + removed.length + changed.length + (cats ? 1 : 0) + (biz ? 1 : 0);
    return { added: added, removed: removed, changed: changed, cats: cats, biz: biz, upload: upload, del: del, count: n, dirty: n > 0 || upload.length > 0 || del.length > 0 };
  }

  function validateAll() {
    var d = S.data, errs = [];
    var n = d.negocio, t = d.tienda;
    if (!String(n.nombre || '').trim()) errs.push('Falta el nombre del negocio.');
    if (!/^\d{10,15}$/.test(String(n.whatsapp || ''))) errs.push('El WhatsApp tiene que tener entre 10 y 15 números, con código de país y sin signos (ej: 5491155550199).');
    if (!/^https?:\/\/[^\s/]+\.[^\s]+$/.test(String(n.sitioUrl || ''))) errs.push('La dirección del sitio tiene que empezar con https:// (ej: https://funnyfoot.netlify.app).');
    ['envioGratisDesde', 'costoEnvio', 'descuentoTransferencia', 'cuotasSinInteres', 'diasCambio'].forEach(function (k) {
      if (typeof t[k] !== 'number' || isNaN(t[k]) || t[k] < 0) errs.push('Revisá el campo numérico "' + k + '" en Negocio y envíos.');
    });
    var ids = {}, slugs = {};
    d.categorias.forEach(function (c) {
      if (!c.nombre) errs.push('Una categoría no tiene nombre.');
      if (slugs['c:' + c.slug]) errs.push('Dos categorías usan la misma dirección web (' + c.slug + ').');
      slugs['c:' + c.slug] = true;
    });
    d.productos.forEach(function (p) {
      var who = 'Producto "' + (p.nombre || p.id) + '": ';
      if (!p.nombre) errs.push(who + 'falta el nombre.');
      if (!(p.precio > 0)) errs.push(who + 'el precio tiene que ser mayor a 0.');
      if (!d.categorias.some(function (c) { return c.id === p.categoria; })) errs.push(who + 'elegí una categoría.');
      if (!p.talles || !p.talles.length) errs.push(who + 'faltan los talles.');
      if (slugs['p:' + p.slug]) errs.push(who + 'otra publicación usa la misma dirección web.');
      slugs['p:' + p.slug] = true;
      if (ids[p.id]) errs.push(who + 'id repetido.');
      ids[p.id] = true;
    });
    return errs;
  }

  /* ------------------------------------------------------------------ fotos */
  function processImage(file) {
    return new Promise(function (resolve, reject) {
      if (!/^image\//.test(file.type)) { reject(new Error('"' + file.name + '" no es una imagen.')); return; }
      if (file.size > 25 * 1024 * 1024) { reject(new Error('"' + file.name + '" pesa más de 25 MB.')); return; }
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var max = 1200, w = img.naturalWidth, hh = img.naturalHeight, k = Math.min(1, max / Math.max(w, hh));
        var cw = Math.max(1, Math.round(w * k)), ch = Math.max(1, Math.round(hh * k));
        var c = document.createElement('canvas'); c.width = cw; c.height = ch;
        var ctx = c.getContext('2d'); ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, cw, ch); ctx.drawImage(img, 0, 0, cw, ch);
        var dataUrl = c.toDataURL('image/jpeg', 0.85);
        URL.revokeObjectURL(url);
        resolve({ dataUrl: dataUrl, base64: dataUrl.split(',')[1] });
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('No se pudo leer "' + file.name + '". Probá con JPG, PNG o WebP.')); };
      img.src = url;
    });
  }

  /* ------------------------------------------------------------------ vistas */
  function renderTop() {
    var box = $('admTopActions');
    if (!S.data) { box.innerHTML = ''; return; }
    var sm = summary();
    box.innerHTML = '<span class="adm-pill' + (sm.dirty ? ' dirty' : '') + '" id="admDirty">' + (sm.dirty ? 'Cambios sin publicar' : 'Todo publicado') + '</span>' +
      '<a class="btn btn-quiet btn-sm" href="' + h(BASE) + '" target="_blank" rel="noopener">Ver sitio</a>' +
      '<button type="button" class="btn btn-quiet btn-sm" data-act="logout">Salir</button>';
  }
  function refreshDirty() {
    var sm = summary(), p = $('admDirty');
    if (p) { p.className = 'adm-pill' + (sm.dirty ? ' dirty' : ''); p.textContent = sm.dirty ? 'Cambios sin publicar' : 'Todo publicado'; }
    var t = document.querySelector('[data-tab="publicar"]');
    if (t) t.textContent = 'Publicar' + (sm.count || sm.upload.length || sm.del.length ? ' (' + Math.max(sm.count, 1) + ')' : '');
  }

  function renderConnect(msg) {
    var remembered = !!(store('local') && store('local').getItem('ff_admin_sesion'));
    $('admMain').innerHTML = '<div class="adm-connect adm-card">' +
      '<h1>Administración</h1>' +
      '<p class="lead">Ingresá con el usuario y el código de administrador para cargar productos, precios y fotos.</p>' +
      '<form id="connectForm" autocomplete="off">' +
      '<div class="field"><label for="cnUser">Usuario</label><input id="cnUser" autocomplete="username" required value="' + h(USUARIO) + '"></div>' +
      '<div class="field"><label for="cnCode">Código de ingreso</label><input id="cnCode" type="password" autocomplete="current-password" required autofocus></div>' +
      '<label class="adm-check" style="margin-bottom:16px"><input type="checkbox" id="cnRemember"' + (remembered ? ' checked' : '') + '><span>Mantener la sesión abierta en este equipo (hasta 12 horas)</span></label>' +
      '<div class="adm-actions"><button type="submit" class="btn btn-pink">Entrar</button><button type="button" class="btn btn-quiet" data-act="demo">Probar sin ingresar</button></div>' +
      '</form>' +
      (msg ? '<div class="adm-msg error" role="alert">' + h(msg) + '</div>' : '') +
      '<p class="hint" style="margin-top:22px">“Probar sin ingresar” abre el panel con el catálogo actual para que lo conozcas. Los cambios no se guardan ni se publican.</p>' +
      '</div>';
  }

  function renderShell() {
    renderTop();
    var sm = summary();
    var tabs = [['productos', 'Productos'], ['categorias', 'Categorías'], ['negocio', 'Negocio y envíos'], ['publicar', 'Publicar' + (sm.dirty ? ' (' + Math.max(sm.count, 1) + ')' : '')]];
    var body = S.tab === 'productos' ? tabProductos() : S.tab === 'categorias' ? tabCategorias() : S.tab === 'negocio' ? tabNegocio() : tabPublicar();
    $('admMain').innerHTML = '<h1>' + h(S.data.negocio.nombre || 'Funny Foot') + '</h1>' +
      '<p class="lead">' + (S.mode === 'demo' ? 'Modo demostración: podés probar todo, pero nada se guarda ni se publica.' : 'Sesión iniciada como ' + h(USUARIO) + '.') + '</p>' +
      '<div class="adm-tabs" role="tablist">' + tabs.map(function (t) {
        return '<button type="button" class="adm-tab" role="tab" aria-selected="' + (S.tab === t[0]) + '" data-tab="' + t[0] + '">' + t[1] + '</button>';
      }).join('') + '</div>' + body;
  }

  /* ---- productos ---- */
  function filteredProducts() {
    var f = S.filter, q = f.q.toLowerCase().trim();
    return S.data.productos.filter(function (p) {
      if (q && p.nombre.toLowerCase().indexOf(q) === -1) return false;
      if (f.cat && p.categoria !== f.cat) return false;
      if (f.estado === 'visibles' && !p.visible) return false;
      if (f.estado === 'ocultos' && p.visible) return false;
      if (f.estado === 'agotados' && !p.agotado) return false;
      return true;
    });
  }
  function productRow(p) {
    var thumb = p.imagenes && p.imagenes[0] ? '<img src="' + h(imgSrc(p.imagenes[0])) + '" alt="">' : SNEAKER.replace('%C', h(p.color || '#ED0B6F'));
    var badges = '';
    if (!p.visible) badges += '<span class="adm-badge gray">Oculto</span>';
    if (p.agotado) badges += '<span class="adm-badge warn">Agotado</span>';
    if (p.destacado) badges += '<span class="adm-badge">Destacado</span>';
    if (p.led) badges += '<span class="adm-badge">LED</span>';
    return '<div class="adm-row' + (p.visible ? '' : ' off') + '"><div class="adm-thumb">' + thumb + '</div>' +
      '<div class="adm-row-main"><b>' + h(p.nombre) + '</b><div class="adm-row-meta"><span>' + h(catName(p.categoria)) + '</span><span>' + money(p.precio) + '</span><span>Talles ' + h(formatTalles(p.talles)) + '</span>' +
      '<span>' + (p.imagenes ? p.imagenes.length : 0) + ' foto' + ((p.imagenes || []).length === 1 ? '' : 's') + '</span>' + badges + '</div></div>' +
      '<div class="adm-row-actions"><button type="button" class="btn btn-quiet btn-sm" data-act="edit-prod" data-id="' + p.id + '">Editar</button></div></div>';
  }
  function productListHtml() {
    var list = filteredProducts();
    if (!S.data.productos.length) return '<div class="adm-empty">Todavía no hay productos. Tocá “Nuevo producto” para cargar el primero.</div>';
    if (!list.length) return '<div class="adm-empty">No hay productos con ese filtro.</div>';
    return '<div class="adm-list">' + list.map(productRow).join('') + '</div>';
  }
  function tabProductos() {
    var f = S.filter;
    var cats = '<option value="">Todas las categorías</option>' + S.data.categorias.map(function (c) { return '<option value="' + h(c.id) + '"' + (f.cat === c.id ? ' selected' : '') + '>' + h(c.nombre) + '</option>'; }).join('');
    var est = [['', 'Todos'], ['visibles', 'Visibles'], ['ocultos', 'Ocultos'], ['agotados', 'Agotados']].map(function (e) { return '<option value="' + e[0] + '"' + (f.estado === e[0] ? ' selected' : '') + '>' + e[1] + '</option>'; }).join('');
    return '<div class="adm-toolbar"><input class="grow" type="search" id="fltQ" data-filter="q" placeholder="Buscar producto…" aria-label="Buscar producto" value="' + h(f.q) + '">' +
      '<select data-filter="cat" aria-label="Categoría">' + cats + '</select><select data-filter="estado" aria-label="Estado">' + est + '</select>' +
      '<button type="button" class="btn btn-pink btn-sm" data-act="new-prod">+ Nuevo producto</button></div>' +
      '<p class="hint" style="margin:-4px 0 14px">' + S.data.productos.length + ' producto' + (S.data.productos.length === 1 ? '' : 's') + ' en total.</p>' +
      '<div id="prodList">' + productListHtml() + '</div>';
  }

  /* ---- categorías ---- */
  function tabCategorias() {
    var rows = S.data.categorias.map(function (c, i) {
      var n = S.data.productos.filter(function (p) { return p.categoria === c.id; }).length;
      return '<div class="adm-row" style="grid-template-columns:1fr auto"><div class="adm-row-main"><b>' + h(c.nombre) + '</b><div class="adm-row-meta"><span>/productos/' + h(c.slug) + '/</span><span>' + n + ' producto' + (n === 1 ? '' : 's') + '</span></div></div>' +
        '<div class="adm-row-actions"><button type="button" class="btn btn-quiet btn-sm" data-act="cat-up" data-id="' + h(c.id) + '"' + (i === 0 ? ' disabled' : '') + ' aria-label="Subir">↑</button>' +
        '<button type="button" class="btn btn-quiet btn-sm" data-act="cat-down" data-id="' + h(c.id) + '"' + (i === S.data.categorias.length - 1 ? ' disabled' : '') + ' aria-label="Bajar">↓</button>' +
        '<button type="button" class="btn btn-quiet btn-sm" data-act="edit-cat" data-id="' + h(c.id) + '">Editar</button></div></div>';
    }).join('');
    return '<div class="adm-toolbar"><span class="hint" style="margin:0">El orden de esta lista es el orden en que aparecen en el sitio.</span><span class="grow"></span><button type="button" class="btn btn-pink btn-sm" data-act="new-cat">+ Nueva categoría</button></div>' +
      (rows ? '<div class="adm-list">' + rows + '</div>' : '<div class="adm-empty">Todavía no hay categorías. Creá una para poder cargar productos.</div>');
  }

  /* ---- negocio ---- */
  function fld(label, path, type, extra) {
    var parts = path.split('.'), v = S.data[parts[0]][parts[1]];
    extra = extra || {};
    var attrs = ' id="b-' + path.replace('.', '-') + '" data-path="' + path + '"' + (type === 'int' ? ' data-type="int" type="number" min="0" step="' + (extra.step || 1) + '"' : (type === 'digits' ? ' data-type="digits" inputmode="numeric"' : ' type="text"')) + ' value="' + h(v == null ? '' : v) + '"';
    var input = type === 'textarea' ? '<textarea id="b-' + path.replace('.', '-') + '" data-path="' + path + '" rows="' + (extra.rows || 3) + '">' + h(v || '') + '</textarea>' : '<input' + attrs + '>';
    return '<div class="field"><label for="b-' + path.replace('.', '-') + '">' + h(label) + '</label>' + input + (extra.hint ? '<small>' + h(extra.hint) + '</small>' : '') + '</div>';
  }
  function tabNegocio() {
    var mp = S.data.tienda.metodosPago || {};
    function chk(k, label) { return '<label class="adm-check"><input type="checkbox" data-path="tienda.metodosPago.' + k + '" ' + (mp[k] ? 'checked' : '') + '><span>' + label + '</span></label>'; }
    return '<div class="adm-card" style="margin-bottom:18px"><h2>Datos del negocio</h2><p class="hint" style="margin:0 0 16px">Se muestran en el pie de página, en Contacto, en Nosotros y en las políticas.</p>' +
      '<div class="adm-grid-2">' + fld('Nombre del negocio', 'negocio.nombre', 'text') + fld('Dirección del sitio', 'negocio.sitioUrl', 'text', { hint: 'Ej: https://funnyfoot.netlify.app (la usan Google y las vistas previas al compartir).' }) + '</div>' +
      '<div class="adm-grid-2">' + fld('WhatsApp (solo números)', 'negocio.whatsapp', 'digits', { hint: 'Con código de país, sin + ni espacios. Ej: 5491155550199' }) + fld('Teléfono como se muestra', 'negocio.telefonoVisible', 'text', { hint: 'Ej: 11 5555-0199' }) + '</div>' +
      '<div class="adm-grid-2">' + fld('Dirección (calle y número)', 'negocio.direccion1', 'text') + fld('Barrio y ciudad', 'negocio.direccion2', 'text') + '</div>' +
      '<div class="adm-grid-2">' + fld('Horarios', 'negocio.horarios', 'text') + fld('Email (opcional)', 'negocio.email', 'text', { hint: 'Si lo completás, aparece en Contacto.' }) + '</div></div>' +
      '<div class="adm-card"><h2>Envíos, pagos y cambios</h2><p class="hint" style="margin:0 0 16px">El carrito y el checkout usan estos valores para calcular el total. También se escriben en las políticas.</p>' +
      '<div class="adm-grid-3">' + fld('Envío gratis desde ($)', 'tienda.envioGratisDesde', 'int', { step: 500, hint: '0 = sin envío gratis.' }) + fld('Costo de envío ($)', 'tienda.costoEnvio', 'int', { step: 100 }) + fld('Descuento por transferencia (%)', 'tienda.descuentoTransferencia', 'int') + '</div>' +
      '<div class="adm-grid-2">' + fld('Cuotas sin interés (0 = ninguna)', 'tienda.cuotasSinInteres', 'int') + fld('Días para cambios', 'tienda.diasCambio', 'int') + '</div>' +
      fld('Plazo de entrega (texto)', 'tienda.plazoEnvio', 'textarea', { rows: 2 }) +
      '<div class="field"><label>Medios de pago que ofrecés</label><div class="adm-checks" style="margin-top:8px">' + chk('transferencia', 'Transferencia bancaria') + chk('mercadopago', 'Mercado Pago (link de pago)') + chk('tarjeta', 'Tarjeta (coordinada)') + chk('efectivo', 'Efectivo al retirar en el local') + '</div></div>' +
      fld('Datos para transferir', 'tienda.datosTransferencia', 'textarea', { rows: 4, hint: 'Titular, CBU/CVU y alias. Se muestran al cliente después de confirmar el pedido. Si lo dejás vacío, le avisás por WhatsApp.' }) + '</div>';
  }

  /* ---- publicar ---- */
  function tabPublicar() {
    var sm = summary(), rows = '';
    function row(label, items) { return items.length ? '<tr><th>' + label + '</th><td>' + items.map(function (p) { return h(p.nombre); }).join('<br>') + '</td></tr>' : ''; }
    rows += row('Productos nuevos', sm.added) + row('Productos modificados', sm.changed) + row('Productos eliminados', sm.removed);
    if (sm.cats) rows += '<tr><th>Categorías</th><td>Hay cambios</td></tr>';
    if (sm.biz) rows += '<tr><th>Negocio y envíos</th><td>Hay cambios</td></tr>';
    if (sm.upload.length) rows += '<tr><th>Fotos nuevas</th><td>' + sm.upload.length + '</td></tr>';
    if (sm.del.length) rows += '<tr><th>Fotos que se eliminan</th><td>' + sm.del.length + '</td></tr>';
    var errs = validateAll();
    return '<div class="adm-card"><h2>Publicar los cambios</h2>' +
      (sm.dirty ? '<table class="adm-table"><tbody>' + rows + '</tbody></table>' : '<p class="lead" style="margin:0">No hay cambios para publicar.</p>') +
      (errs.length && sm.dirty ? '<div class="adm-msg error" role="alert"><b>Antes de publicar corregí esto:</b><br>' + errs.map(h).join('<br>') + '</div>' : '') +
      '<div class="field" style="margin-top:18px"><label for="pubMsg">Descripción del cambio</label><input id="pubMsg" value="Actualizar el catálogo desde el panel"></div>' +
      '<div class="adm-actions"><button type="button" class="btn btn-pink" data-act="publish"' + (!sm.dirty || errs.length || S.publishing ? ' disabled' : '') + '>' + (S.mode === 'demo' ? 'Publicar (no disponible en demostración)' : 'Publicar cambios') + '</button>' +
      '<button type="button" class="btn btn-quiet" data-act="discard"' + (!sm.dirty ? ' disabled' : '') + '>Descartar cambios</button></div>' +
      '<ul class="adm-log" id="pubLog" hidden></ul><div id="pubResult"></div>' +
      '<p class="hint" style="margin-top:16px">Al publicar, Netlify tarda 1 o 2 minutos en actualizar el sitio. Cada publicación cuenta como un deploy en Netlify: conviene cargar varios cambios juntos y publicar una sola vez.</p></div>';
  }

  /* ---------------------------------------------------------------- editor de producto */
  function openModal(html) { $('admModal').innerHTML = '<div class="adm-modal"><div class="modal show" role="dialog" aria-modal="true">' + html + '</div></div>'; document.body.style.overflow = 'hidden'; }
  function closeModal() {
    if (S.editing && S.editing.added) { S.editing.added.forEach(function (p) { var used = false; S.data.productos.forEach(function (x) { if ((x.imagenes || []).indexOf(p) !== -1) used = true; }); if (!used) delete S.pending[p]; }); }
    S.editing = null; $('admModal').innerHTML = ''; document.body.style.overflow = '';
  }
  function blankProduct() {
    return { id: nextProductId(), slug: '', nombre: '', categoria: (S.data.categorias[0] || {}).id || '', precio: 0, talles: [], color: '#ED0B6F', colorNombre: '', led: false, descripcion: '', imagenes: [], visible: true, agotado: false, destacado: false };
  }
  function openProductEditor(id, dup) {
    var src = id != null ? S.data.productos.filter(function (p) { return p.id === id; })[0] : null;
    var draft = src ? clone(src) : blankProduct();
    var isNew = !src;
    if (src && dup) { draft = clone(src); draft.id = nextProductId(); draft.nombre = src.nombre + ' (copia)'; draft.slug = ''; isNew = true; }
    S.editing = { kind: 'prod', isNew: isNew, draft: draft, added: [], origId: src && !dup ? src.id : null };
    if (!S.data.categorias.length) { openModal('<div class="modal-card"><div class="modal-head"><h2>Primero creá una categoría</h2><button type="button" class="modal-close" data-act="cancel-modal" aria-label="Cerrar">✕</button></div><p>Para cargar un producto necesitás al menos una categoría. Andá a la pestaña Categorías.</p></div>'); return; }
    var cats = S.data.categorias.map(function (c) { return '<option value="' + h(c.id) + '"' + (draft.categoria === c.id ? ' selected' : '') + '>' + h(c.nombre) + '</option>'; }).join('');
    openModal('<div class="modal-card"><div class="modal-head"><h2>' + (isNew ? 'Nuevo producto' : 'Editar producto') + '</h2><button type="button" class="modal-close" data-act="cancel-modal" aria-label="Cerrar">✕</button></div>' +
      '<form id="prodForm" novalidate>' +
      '<div class="field"><label for="ed-nombre">Nombre del producto</label><input id="ed-nombre" maxlength="140" value="' + h(draft.nombre) + '"></div>' +
      '<div class="adm-grid-2"><div class="field"><label for="ed-cat">Categoría</label><select id="ed-cat">' + cats + '</select></div>' +
      '<div class="field"><label for="ed-precio">Precio ($)</label><input id="ed-precio" type="number" min="0" step="100" inputmode="numeric" value="' + (draft.precio || '') + '"></div></div>' +
      '<div class="field"><label for="ed-talles">Talles</label><input id="ed-talles" value="' + h(formatTalles(draft.talles)) + '" placeholder="Ej: 23-28  o  23, 24, 26-28"><small>Escribí un rango o una lista. Solo se ofrecen estos talles.</small><div class="adm-chips" id="tallesPreview"></div></div>' +
      '<div class="adm-grid-2"><div class="field"><label for="ed-color">Color</label><input id="ed-color" type="color" value="' + h(/^#[0-9a-fA-F]{6}$/.test(draft.color) ? draft.color : '#ED0B6F') + '"><small>Se usa en la ilustración cuando el producto no tiene fotos.</small></div>' +
      '<div class="field"><label for="ed-colorNombre">Nombre del color</label><input id="ed-colorNombre" maxlength="40" value="' + h(draft.colorNombre) + '" placeholder="Ej: Lila"></div></div>' +
      '<div class="field"><label for="ed-desc">Descripción</label><textarea id="ed-desc" rows="4" maxlength="1500" placeholder="Materiales, detalles, cuidados… (opcional)">' + h(draft.descripcion) + '</textarea></div>' +
      '<div class="adm-checks">' +
      '<label class="adm-check"><input type="checkbox" id="ed-visible"' + (draft.visible ? ' checked' : '') + '><span><b>Mostrar en la tienda</b><br><small class="hint">Si lo desmarcás, el producto queda oculto.</small></span></label>' +
      '<label class="adm-check"><input type="checkbox" id="ed-agotado"' + (draft.agotado ? ' checked' : '') + '><span><b>Agotado</b><br><small class="hint">Se muestra pero no se puede comprar.</small></span></label>' +
      '<label class="adm-check"><input type="checkbox" id="ed-destacado"' + (draft.destacado ? ' checked' : '') + '><span><b>Destacado en el inicio</b></span></label>' +
      '<label class="adm-check"><input type="checkbox" id="ed-led"' + (draft.led ? ' checked' : '') + '><span><b>Tiene luz LED</b></span></label></div>' +
      '<div class="field"><label>Fotos (hasta ' + MAX_FOTOS + ')</label><div id="edPhotos"></div>' +
      '<label class="adm-drop" id="edDrop"><input type="file" id="edFiles" accept="image/*" multiple><b>Elegí fotos</b> o arrastralas acá<br><small>JPG, PNG o WebP. Se optimizan solas. La primera es la principal.</small></label><div id="edPhotoMsg"></div></div>' +
      '<details style="margin-bottom:16px"><summary style="cursor:pointer;font-weight:700;font-size:13.5px">Dirección web del producto</summary><div class="field" style="margin-top:10px"><label for="ed-slug">Dirección (URL)</label><input id="ed-slug" value="' + h(draft.slug) + '" placeholder="Se arma sola con el nombre"><small>/producto/<span id="slugPreview"></span>/. No la cambies si el producto ya está publicado: se rompen los enlaces.</small></div></details>' +
      '<div class="adm-msg error" id="edMsg" role="alert" hidden></div>' +
      '<div class="adm-actions" style="margin-top:18px"><button type="submit" class="btn btn-pink">Guardar producto</button><button type="button" class="btn btn-quiet" data-act="cancel-modal">Cancelar</button>' +
      (!isNew ? '<button type="button" class="btn btn-quiet" data-act="dup-prod">Duplicar</button><span id="delBox"><button type="button" class="btn btn-quiet" data-act="del-ask">Eliminar</button></span>' : '') + '</div></form></div>');
    updateTallesPreview(); renderPhotos();
  }
  function updateTallesPreview() {
    var el = $('ed-talles'), box = $('tallesPreview'); if (!el || !box) return;
    var r = parseTalles(el.value);
    box.innerHTML = el.value.trim() === '' ? '' : (r.bad ? '<span style="background:var(--spark);color:#1B1226">Revisá los talles: usá números entre 14 y 50</span>' : r.list.map(function (t) { return '<span>' + t + '</span>'; }).join(''));
  }
  function renderPhotos() {
    var box = $('edPhotos'); if (!box || !S.editing) return;
    var im = S.editing.draft.imagenes;
    box.innerHTML = im.length ? '<div class="adm-photos">' + im.map(function (p, i) {
      return '<div class="adm-photo' + (i === 0 ? ' main' : '') + '"><img src="' + h(imgSrc(p)) + '" alt="Foto ' + (i + 1) + '">' + (i === 0 ? '<span class="tag">Principal</span>' : '') +
        '<div class="adm-photo-actions">' + (i > 0 ? '<button type="button" data-act="photo-main" data-i="' + i + '">Principal</button>' : '') + '<button type="button" data-act="photo-del" data-i="' + i + '">Quitar</button></div></div>';
    }).join('') + '</div>' : '<p class="hint" style="margin:0 0 10px">Todavía no cargaste fotos. Mientras tanto se muestra una ilustración.</p>';
  }
  async function addFiles(files) {
    var ed = S.editing; if (!ed || ed.kind !== 'prod') return;
    var msg = $('edPhotoMsg'); msg.innerHTML = '';
    var errs = [];
    for (var i = 0; i < files.length; i++) {
      if (ed.draft.imagenes.length >= MAX_FOTOS) { errs.push('Máximo ' + MAX_FOTOS + ' fotos por producto.'); break; }
      try {
        var r = await processImage(files[i]);
        var path = 'assets/productos/p' + ed.draft.id + '-' + rand(6) + '.jpg';
        S.pending[path] = r; ed.added.push(path); ed.draft.imagenes.push(path);
      } catch (e) { errs.push(e.message); }
    }
    renderPhotos();
    if (errs.length) msg.innerHTML = '<div class="adm-msg error" role="alert">' + errs.map(h).join('<br>') + '</div>';
  }

  function saveProduct() {
    var ed = S.editing, d = ed.draft, msg = $('edMsg');
    var v = function (id) { return $(id).value.trim(); };
    var errs = [];
    var nombre = v('ed-nombre'), precio = parseInt($('ed-precio').value, 10), tl = parseTalles($('ed-talles').value);
    if (nombre.length < 2) errs.push('Escribí el nombre del producto.');
    if (!(precio > 0)) errs.push('Ingresá un precio mayor a 0.');
    if (tl.bad) errs.push('Revisá los talles: usá números entre 14 y 50, por ejemplo 23-28.');
    if (!v('ed-cat')) errs.push('Elegí una categoría.');
    var slug = slugify(v('ed-slug') || nombre);
    S.data.productos.forEach(function (p) { if (p.id !== d.id && p.slug === slug) { slug = slug + '-' + d.id; } });
    if (errs.length) { msg.innerHTML = errs.map(h).join('<br>'); msg.hidden = false; msg.scrollIntoView({ block: 'center' }); return; }
    var color = $('ed-color').value;
    var out = {
      id: d.id, slug: ed.isNew ? slug : (d.slug || slug), nombre: nombre, categoria: v('ed-cat'), precio: precio, talles: tl.list, color: color,
      colorNombre: v('ed-colorNombre'), led: $('ed-led').checked, descripcion: $('ed-desc').value.trim(), imagenes: d.imagenes.slice(),
      visible: $('ed-visible').checked, agotado: $('ed-agotado').checked, destacado: $('ed-destacado').checked
    };
    if (!ed.isNew && $('ed-slug').value.trim()) out.slug = slugify($('ed-slug').value);
    var idx = -1; S.data.productos.forEach(function (p, i) { if (p.id === out.id) idx = i; });
    if (idx >= 0) S.data.productos[idx] = out; else S.data.productos.push(out);
    ed.added = [];   // las fotos agregadas ya quedan asociadas al producto
    closeModal(); renderShell(); toast('Producto guardado. Recordá publicar los cambios.');
  }

  /* ---------------------------------------------------------------- editor de categoría */
  function openCategoryEditor(id) {
    var src = id ? S.data.categorias.filter(function (c) { return c.id === id; })[0] : null;
    var d = src ? clone(src) : { id: '', slug: '', nombre: '', h1: '', intro: '', resumen: '', icono: 'spark' };
    S.editing = { kind: 'cat', isNew: !src, draft: d, added: [] };
    var icons = ICONOS.map(function (i) { return '<option value="' + i[0] + '"' + (d.icono === i[0] ? ' selected' : '') + '>' + i[1] + '</option>'; }).join('');
    var n = src ? S.data.productos.filter(function (p) { return p.categoria === src.id; }).length : 0;
    openModal('<div class="modal-card"><div class="modal-head"><h2>' + (src ? 'Editar categoría' : 'Nueva categoría') + '</h2><button type="button" class="modal-close" data-act="cancel-modal" aria-label="Cerrar">✕</button></div>' +
      '<form id="catForm" novalidate>' +
      '<div class="field"><label for="ec-nombre">Nombre</label><input id="ec-nombre" maxlength="60" value="' + h(d.nombre) + '" placeholder="Ej: Sandalias"></div>' +
      '<div class="field"><label for="ec-h1">Título de la página (opcional)</label><input id="ec-h1" maxlength="120" value="' + h(d.h1 && d.h1 !== d.nombre ? d.h1 : '') + '" placeholder="Ej: Sandalias para niñas y niños"></div>' +
      '<div class="field"><label for="ec-intro">Texto de introducción</label><textarea id="ec-intro" rows="3" maxlength="400">' + h(d.intro) + '</textarea></div>' +
      '<div class="adm-grid-2"><div class="field"><label for="ec-resumen">Frase corta para el inicio</label><input id="ec-resumen" maxlength="80" value="' + h(d.resumen) + '"></div>' +
      '<div class="field"><label for="ec-icono">Ícono en el inicio</label><select id="ec-icono">' + icons + '</select></div></div>' +
      '<div class="field"><label for="ec-slug">Dirección web</label><input id="ec-slug" value="' + h(d.slug) + '" placeholder="Se arma sola con el nombre"><small>/productos/<span id="csPreview"></span>/. ' + (src ? 'Si la cambiás, los enlaces viejos dejan de funcionar.' : '') + '</small></div>' +
      '<div class="adm-msg error" id="ecMsg" role="alert" hidden></div>' +
      '<div class="adm-actions" style="margin-top:18px"><button type="submit" class="btn btn-pink">Guardar categoría</button><button type="button" class="btn btn-quiet" data-act="cancel-modal">Cancelar</button>' +
      (src ? (n ? '<span class="hint" style="margin:0">No se puede eliminar: tiene ' + n + ' producto' + (n === 1 ? '' : 's') + '.</span>' : '<span id="delBox"><button type="button" class="btn btn-quiet" data-act="delc-ask">Eliminar</button></span>') : '') + '</div></form></div>');
    updateSlugPreviews();
  }
  function saveCategory() {
    var ed = S.editing, d = ed.draft, msg = $('ecMsg');
    var nombre = $('ec-nombre').value.trim();
    if (nombre.length < 2) { msg.textContent = 'Escribí el nombre de la categoría.'; msg.hidden = false; return; }
    var slug = slugify($('ec-slug').value || nombre);
    var clash = S.data.categorias.some(function (c) { return c.id !== d.id && c.slug === slug; });
    if (clash) { msg.textContent = 'Ya existe otra categoría con esa dirección web. Cambiá el nombre o la dirección.'; msg.hidden = false; return; }
    var out = { id: d.id || (slugify(nombre) + '-' + rand(3)), slug: slug, nombre: nombre, h1: $('ec-h1').value.trim() || nombre, intro: $('ec-intro').value.trim(),
      resumen: $('ec-resumen').value.trim(), icono: $('ec-icono').value };
    if (d.titulo) out.titulo = d.titulo;
    if (d.descripcion) out.descripcion = d.descripcion;
    var idx = -1; S.data.categorias.forEach(function (c, i) { if (c.id === out.id) idx = i; });
    if (idx >= 0) S.data.categorias[idx] = out; else S.data.categorias.push(out);
    closeModal(); renderShell(); toast('Categoría guardada. Recordá publicar los cambios.');
  }
  function updateSlugPreviews() {
    var a = $('slugPreview'), b = $('csPreview');
    if (a) a.textContent = slugify(($('ed-slug').value || $('ed-nombre').value));
    if (b) b.textContent = slugify(($('ec-slug').value || $('ec-nombre').value));
  }

  /* ---------------------------------------------------------------- publicar */
  async function doPublish() {
    if (S.publishing) return;
    if (S.mode === 'demo') { toast('En modo demostración no se publica. Ingresá con el usuario y el código.'); return; }
    var errs = validateAll(); if (errs.length) { renderShell(); return; }
    var sm = summary(); if (!sm.dirty) return;
    var message = ($('pubMsg') && $('pubMsg').value.trim()) || 'Actualizar el catálogo desde el panel';
    S.publishing = true;
    var log = $('pubLog'), result = $('pubResult');
    log.hidden = false; log.innerHTML = ''; result.innerHTML = '';
    var pub = document.querySelector('[data-act="publish"]'); if (pub) pub.disabled = true;
    function step(t) { var li = document.createElement('li'); li.className = 'run'; li.textContent = t; log.appendChild(li); var prev = log.children[log.children.length - 2]; if (prev) prev.className = ''; }
    var text = JSON.stringify(S.data, null, 2) + '\n';
    var files = [{ path: 'datos/productos.json', text: text, isData: true }];
    sm.upload.forEach(function (p) { files.push({ path: p, base64: S.pending[p].base64 }); });
    sm.del.forEach(function (p) { files.push({ path: p, remove: true }); });
    try {
      var r = await publishViaApi(files, message, step);
      log.lastChild.className = '';
      S.orig = JSON.stringify(JSON.parse(text)); S.pending = {};
      // el sha del archivo de datos pasa a ser el del blob subido
      S.baseSha = r.jsonSha || S.baseSha;
      result.innerHTML = '<div class="adm-msg ok" role="status"><b>¡Cambios publicados!</b><br>El sitio se actualiza en 1 o 2 minutos.</div>';
      renderTop(); refreshDirty();
      toast('Cambios publicados');
    } catch (e) {
      if (e.status === 401 && e.code !== 'credenciales') { logout(explain(e)); S.publishing = false; return; }
      result.innerHTML = '<div class="adm-msg error" role="alert"><b>No se pudo publicar.</b><br>' + h(explain(e)) + '</div>';
      if (pub) pub.disabled = false;
    }
    S.publishing = false;
  }

  /* ---------------------------------------------------------------- arranque / ingreso */
  function startWith(text, sha, mode) {
    S.data = normalize(JSON.parse(text)); S.orig = JSON.stringify(JSON.parse(text)); S.baseSha = sha || '';
    S.mode = mode; S.pending = {}; S.tab = 'productos'; S.editing = null; S.filter = { q: '', cat: '', estado: '' };
    renderShell();
  }
  function saveSession(token, remember) {
    var ss = store('session'), ls = store('local');
    try { if (ss) ss.setItem('ff_admin_sesion', token); if (remember && ls) ls.setItem('ff_admin_sesion', token); else if (ls) ls.removeItem('ff_admin_sesion'); } catch (e) {}
  }
  async function enterWithSession() {
    var r = await api('load');
    startWith(r.text, r.sha, 'sitio');
  }
  async function doConnect() {
    var user = $('cnUser').value.trim(), code = $('cnCode').value;
    var btn = document.querySelector('#connectForm button[type=submit]'); btn.disabled = true; btn.textContent = 'Entrando…';
    try {
      var r = await api('login', { usuario: user, codigo: code });
      S.session = r.token; saveSession(r.token, $('cnRemember').checked);
      await enterWithSession();
    } catch (e) { S.session = ''; renderConnect(explain(e)); }
  }
  async function doDemo() {
    try {
      var res = await fetch(BASE + 'datos/productos.json', { cache: 'no-store' });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      startWith(await res.text(), '', 'demo');
    } catch (e) { renderConnect('No se pudo cargar el catálogo de demostración.'); }
  }
  function logout(msg) {
    var ss = store('session'), ls = store('local');
    try { if (ss) ss.removeItem('ff_admin_sesion'); if (ls) ls.removeItem('ff_admin_sesion'); } catch (e) {}
    S.data = null; S.session = ''; S.editing = null; $('admModal').innerHTML = ''; document.body.style.overflow = '';
    renderTop(); renderConnect(typeof msg === 'string' ? msg : '');
  }

  /* ---------------------------------------------------------------- eventos */
  document.addEventListener('click', function (e) {
    var tab = e.target.closest && e.target.closest('[data-tab]');
    if (tab) { S.tab = tab.getAttribute('data-tab'); renderShell(); return; }
    var a = e.target.closest && e.target.closest('[data-act]');
    if (!a) return;
    var act = a.getAttribute('data-act'), id = a.getAttribute('data-id'), ed = S.editing;
    switch (act) {
      case 'demo': doDemo(); break;
      case 'logout': logout(); break;
      case 'new-prod': openProductEditor(null); break;
      case 'edit-prod': openProductEditor(parseInt(id, 10)); break;
      case 'dup-prod': { var oid = ed && ed.origId; closeModal(); if (oid != null) openProductEditor(oid, true); break; }
      case 'cancel-modal': closeModal(); break;
      case 'photo-del': ed.draft.imagenes.splice(parseInt(a.getAttribute('data-i'), 10), 1); renderPhotos(); break;
      case 'photo-main': { var i = parseInt(a.getAttribute('data-i'), 10), im = ed.draft.imagenes; im.unshift(im.splice(i, 1)[0]); renderPhotos(); break; }
      case 'del-ask': $('delBox').innerHTML = '<span class="adm-confirm">¿Eliminar este producto? <button type="button" class="btn btn-danger btn-sm" data-act="del-yes">Sí, eliminar</button><button type="button" class="btn btn-quiet btn-sm" data-act="del-no">No</button></span>'; break;
      case 'del-no': $('delBox').innerHTML = '<button type="button" class="btn btn-quiet" data-act="del-ask">Eliminar</button>'; break;
      case 'del-yes': { var pid = ed.origId; S.data.productos = S.data.productos.filter(function (p) { return p.id !== pid; }); closeModal(); renderShell(); toast('Producto eliminado. Recordá publicar los cambios.'); break; }
      case 'new-cat': openCategoryEditor(null); break;
      case 'edit-cat': openCategoryEditor(id); break;
      case 'cat-up': case 'cat-down': {
        var arr = S.data.categorias, ix = arr.map(function (c) { return c.id; }).indexOf(id), jx = act === 'cat-up' ? ix - 1 : ix + 1;
        if (ix >= 0 && jx >= 0 && jx < arr.length) { var t = arr[ix]; arr[ix] = arr[jx]; arr[jx] = t; renderShell(); }
        break;
      }
      case 'delc-ask': $('delBox').innerHTML = '<span class="adm-confirm">¿Eliminar esta categoría? <button type="button" class="btn btn-danger btn-sm" data-act="delc-yes">Sí, eliminar</button><button type="button" class="btn btn-quiet btn-sm" data-act="delc-no">No</button></span>'; break;
      case 'delc-no': $('delBox').innerHTML = '<button type="button" class="btn btn-quiet" data-act="delc-ask">Eliminar</button>'; break;
      case 'delc-yes': { var cid = ed.draft.id; S.data.categorias = S.data.categorias.filter(function (c) { return c.id !== cid; }); closeModal(); renderShell(); toast('Categoría eliminada. Recordá publicar los cambios.'); break; }
      case 'publish': doPublish(); break;
      case 'discard': {
        if (!a.getAttribute('data-sure')) { a.setAttribute('data-sure', '1'); a.textContent = 'Confirmar: descartar todo'; break; }
        S.data = normalize(JSON.parse(S.orig)); S.pending = {}; renderShell(); toast('Cambios descartados'); break;
      }
    }
  });

  document.addEventListener('submit', function (e) {
    e.preventDefault();
    if (e.target.id === 'connectForm') doConnect();
    else if (e.target.id === 'prodForm') saveProduct();
    else if (e.target.id === 'catForm') saveCategory();
  });

  document.addEventListener('input', function (e) {
    var t = e.target;
    if (t.id === 'ed-talles') updateTallesPreview();
    if (t.id === 'ed-slug' || t.id === 'ed-nombre' || t.id === 'ec-slug' || t.id === 'ec-nombre') updateSlugPreviews();
    if (t.getAttribute && t.getAttribute('data-filter')) {
      S.filter[t.getAttribute('data-filter')] = t.value;
      var box = $('prodList'); if (box) box.innerHTML = productListHtml();
      return;
    }
    var path = t.getAttribute && t.getAttribute('data-path');
    if (path) {
      var parts = path.split('.'), obj = S.data, k;
      for (k = 0; k < parts.length - 1; k++) obj = obj[parts[k]];
      var key = parts[parts.length - 1], val;
      if (t.type === 'checkbox') val = t.checked;
      else if (t.getAttribute('data-type') === 'int') { val = parseFloat(t.value); if (isNaN(val)) val = 0; }
      else if (t.getAttribute('data-type') === 'digits') { val = t.value.replace(/\D/g, ''); }
      else val = t.value;
      obj[key] = val;
      refreshDirty();
    }
  });
  document.addEventListener('change', function (e) {
    var t = e.target;
    /* el buscador ya se aplicó en 'input'; volver a dibujar acá haría perder el primer clic en "Editar" */
    if (t.getAttribute && t.getAttribute('data-filter')) { if (t.tagName === 'SELECT') { S.filter[t.getAttribute('data-filter')] = t.value; var box = $('prodList'); if (box) box.innerHTML = productListHtml(); } return; }
    if (t.type === 'checkbox' && t.getAttribute('data-path')) { var p = t.getAttribute('data-path').split('.'), o = S.data; for (var i = 0; i < p.length - 1; i++) o = o[p[i]]; o[p[p.length - 1]] = t.checked; refreshDirty(); return; }
    if (t.id === 'edFiles') { addFiles(Array.prototype.slice.call(t.files)); t.value = ''; }
  });
  document.addEventListener('dragover', function (e) { var d = e.target.closest && e.target.closest('#edDrop'); if (d) { e.preventDefault(); d.classList.add('over'); } });
  document.addEventListener('dragleave', function (e) { var d = e.target.closest && e.target.closest('#edDrop'); if (d) d.classList.remove('over'); });
  document.addEventListener('drop', function (e) {
    var d = e.target.closest && e.target.closest('#edDrop');
    if (d) { e.preventDefault(); d.classList.remove('over'); addFiles(Array.prototype.slice.call(e.dataTransfer.files)); }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && S.editing) closeModal(); });
  window.addEventListener('beforeunload', function (e) {
    if (S.data && S.mode === 'sitio' && summary().dirty) { e.preventDefault(); e.returnValue = ''; }
  });

  /* ---------------------------------------------------------------- inicio */
  (function init() {
    renderTop();
    var tok = sessionToken();
    if (sessionValid(tok)) {
      S.session = tok;
      $('admMain').innerHTML = '<p class="adm-loading">Retomando tu sesión…</p>';
      enterWithSession().catch(function (e) { S.session = ''; renderConnect(e && e.status === 401 ? '' : explain(e)); });
    } else { renderConnect(); }
  })();
})();
