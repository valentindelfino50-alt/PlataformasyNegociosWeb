/* Funny Foot: carrito, galería de producto, buscador, menú y medición de Google.
   Usa el catálogo generado en assets/js/catalogo.js (window.FF_CATALOGO). */
(function () {
  'use strict';

  var CFG = window.FUNNYFOOT || {};
  var CAT = window.FF_CATALOGO || { config: {}, productos: [] };
  var CONF = CAT.config || {};
  var MAX_QTY = 10;

  var metaBase = document.querySelector('meta[name="ff-base"]');
  var BASE = metaBase ? metaBase.content : '/';
  var PREVIEW = !!document.querySelector('meta[name="ff-preview"]');
  /* En la vista previa de Claude las páginas son archivos (index.html); en el sitio real, carpetas. */
  function pageUrl(p) { return BASE + p + (PREVIEW ? 'index.html' : ''); }
  function assetUrl(p) { return BASE + p; }

  function money(n) { return '$' + Math.round(n).toLocaleString('es-AR'); }
  function byId(id) {
    for (var i = 0; i < CAT.productos.length; i++) { if (CAT.productos[i].id === id) return CAT.productos[i]; }
    return null;
  }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function $(id) { return document.getElementById(id); }

  /* ---------- medición (Google Analytics / Google Ads) ---------- */
  function loadGoogleTag() {
    var ids = [CFG.GA4_ID, CFG.ADS_ID].filter(Boolean);
    if (!ids.length) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ids[0]);
    document.head.appendChild(s);
    window.gtag('js', new Date());
    ids.forEach(function (id) { window.gtag('config', id); });
  }
  function track(name, params) { try { if (window.gtag) window.gtag('event', name, params || {}); } catch (e) {} }
  function convert(label, extra) {
    try {
      if (window.gtag && CFG.ADS_ID && label) {
        var p = { send_to: CFG.ADS_ID + '/' + label };
        for (var k in (extra || {})) { p[k] = extra[k]; }
        window.gtag('event', 'conversion', p);
      }
    } catch (e) {}
  }
  loadGoogleTag();

  /* ---------- carrito ---------- */
  var CART = [];
  var removedMsg = false;
  try {
    var saved = JSON.parse(localStorage.getItem('funnyfoot_cart') || '[]');
    if (Array.isArray(saved)) {
      saved.forEach(function (i) {
        var p = i && byId(i.id);
        var size = i && parseInt(i.size, 10);
        if (!p || p.agotado || !size || p.talles.indexOf(size) === -1 || !(i.qty > 0)) { removedMsg = true; return; }
        CART.push({ id: p.id, size: String(size), qty: Math.min(parseInt(i.qty, 10) || 1, MAX_QTY) });
      });
    }
  } catch (e) { CART = []; }
  function saveCart() { try { localStorage.setItem('funnyfoot_cart', JSON.stringify(CART)); } catch (e) {} }

  function subtotal() { return CART.reduce(function (s, i) { return s + byId(i.id).precio * i.qty; }, 0); }
  function count() { return CART.reduce(function (n, i) { return n + i.qty; }, 0); }

  /* Cálculo único del total, usado por el carrito y por el checkout. */
  function totals(entrega, pago) {
    var sub = subtotal();
    var desc = (pago === 'transferencia' && CONF.descuentoTransferencia) ? Math.round(sub * CONF.descuentoTransferencia / 100) : 0;
    var envio = 0;
    if (entrega !== 'retiro' && sub > 0) {
      envio = (CONF.envioGratisDesde && sub >= CONF.envioGratisDesde) ? 0 : (CONF.costoEnvio || 0);
    }
    return { subtotal: sub, descuento: desc, envio: envio, total: sub - desc + envio };
  }

  function waLink(text) {
    return 'https://wa.me/' + encodeURIComponent(CONF.whatsapp || '') + (text ? '?text=' + encodeURIComponent(text) : '');
  }
  function orderLines() {
    return CART.map(function (i) {
      var p = byId(i.id);
      return i.qty + ' x ' + p.nombre + ' (talle ' + i.size + ') - ' + money(p.precio * i.qty);
    });
  }
  function quickOrderText() {
    return ['Hola ' + (CONF.nombre || '') + '! Quiero hacer este pedido:', ''].concat(orderLines().map(function (l) { return '• ' + l; }),
      ['', 'Total de productos: ' + money(subtotal()), '', 'Mi nombre:', 'Entrega (envío a domicilio o retiro en el local):']).join('\n');
  }

  var toastTimer;
  function toast(msg) {
    var t = $('toast'); if (!t) return;
    $('toastMsg').textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('show'); }, 2600);
  }

  var SVGNS = 'http://www.w3.org/2000/svg';
  function thumb(p) {
    var box = el('div', 'ci-media');
    if (p.imagen) {
      var img = el('img'); img.src = assetUrl(p.imagen); img.alt = ''; img.loading = 'lazy'; box.appendChild(img);
    } else {
      var svg = document.createElementNS(SVGNS, 'svg'); svg.setAttribute('viewBox', '0 0 120 80');
      svg.style.color = p.color || '#ED0B6F';
      var use = document.createElementNS(SVGNS, 'use'); use.setAttribute('href', '#ic-sneaker'); svg.appendChild(use); box.appendChild(svg);
    }
    return box;
  }

  function renderCart() {
    var badge = $('cartCount');
    if (badge) { var n = count(); badge.textContent = n; badge.hidden = n === 0; }
    var body = $('drawerBody'), foot = $('drawerFoot');
    if (!body || !foot) return;
    body.textContent = ''; foot.textContent = '';
    if (!CART.length) {
      var empty = el('div', 'drawer-empty');
      empty.appendChild(el('p', null, 'Todavía no agregaste productos.'));
      empty.appendChild(el('p', null, 'Elegí un talle y tocá + en el modelo que te guste.'));
      body.appendChild(empty);
      return;
    }
    CART.forEach(function (item, idx) {
      var p = byId(item.id);
      var row = el('div', 'cart-item');
      row.appendChild(thumb(p));
      var info = el('div', 'ci-info');
      info.appendChild(el('b', null, p.nombre));
      info.appendChild(el('span', null, 'Talle ' + item.size + ' · ' + money(p.precio)));
      var r = el('div', 'ci-row');
      var step = el('div', 'qty-stepper');
      var minus = el('button', null, '−'); minus.type = 'button'; minus.setAttribute('aria-label', 'Quitar una unidad');
      minus.addEventListener('click', function () { changeQty(idx, -1); });
      var plus = el('button', null, '+'); plus.type = 'button'; plus.setAttribute('aria-label', 'Sumar una unidad');
      plus.disabled = item.qty >= MAX_QTY;
      plus.addEventListener('click', function () { changeQty(idx, 1); });
      step.appendChild(minus); step.appendChild(el('span', null, String(item.qty))); step.appendChild(plus);
      var rm = el('button', 'ci-remove', 'Quitar'); rm.type = 'button';
      rm.addEventListener('click', function () { CART.splice(idx, 1); saveCart(); renderCart(); });
      r.appendChild(step); r.appendChild(el('b', null, money(p.precio * item.qty))); r.appendChild(rm);
      info.appendChild(r);
      row.appendChild(info);
      body.appendChild(row);
    });
    var rowT = el('div', 'row total');
    rowT.appendChild(el('span', null, 'Subtotal')); rowT.appendChild(el('span', null, money(subtotal())));
    foot.appendChild(rowT);
    foot.appendChild(el('p', 'drawer-note', 'El envío y el medio de pago se eligen al finalizar la compra.'));
    var go = el('a', 'btn btn-pink btn-block', 'Finalizar compra');
    go.id = 'goCheckout'; go.href = pageUrl('checkout/');
    foot.appendChild(go);
    var wa = el('a', 'drawer-wa', 'Prefiero pedir por WhatsApp');
    wa.id = 'waOrder'; wa.target = '_blank'; wa.rel = 'noopener'; wa.href = waLink(quickOrderText());
    wa.addEventListener('click', function () { track('whatsapp_pedido', { value: subtotal(), currency: 'ARS' }); convert(CFG.ADS_LABEL_WHATSAPP); });
    foot.appendChild(wa);
  }
  function changeQty(idx, d) {
    CART[idx].qty += d;
    if (CART[idx].qty <= 0) CART.splice(idx, 1);
    else if (CART[idx].qty > MAX_QTY) CART[idx].qty = MAX_QTY;
    saveCart(); renderCart();
  }
  function addToCart(id, size) {
    var p = byId(id);
    if (!p) return;
    if (p.agotado) { toast('Este producto está agotado'); return; }
    var found = null;
    CART.forEach(function (i) { if (i.id === id && i.size === size) found = i; });
    if (found) {
      if (found.qty >= MAX_QTY) { toast('Máximo ' + MAX_QTY + ' unidades por modelo y talle'); return; }
      found.qty++;
    } else { CART.push({ id: id, size: size, qty: 1 }); }
    saveCart(); renderCart();
    track('add_to_cart', { currency: 'ARS', value: p.precio, items: [{ item_id: String(p.id), item_name: p.nombre, price: p.precio, quantity: 1 }] });
    toast('¡Agregado al carrito!');
  }
  function clearCart() { CART = []; saveCart(); renderCart(); }

  /* cajón del carrito */
  var drawer = $('cartDrawer'), overlay = $('overlay'), lastFocus = null;
  function openDrawer() {
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.classList.add('open'); overlay.classList.add('show'); drawer.setAttribute('aria-hidden', 'false');
    var c = $('closeDrawer'); if (c) c.focus();
  }
  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.remove('open'); overlay.classList.remove('show'); drawer.setAttribute('aria-hidden', 'true');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  var cartBtn = $('cartBtn'); if (cartBtn) cartBtn.addEventListener('click', openDrawer);
  var closeBtn = $('closeDrawer'); if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (overlay) overlay.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closeDrawer(); closeNav(); } });

  /* botones "agregar" de tarjetas y de la ficha de producto */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('[data-add]') : null;
    if (!btn) return;
    var id = parseInt(btn.getAttribute('data-add'), 10);
    var sel = $('size-' + id);
    if (!sel || !sel.value) { if (sel) { sel.style.borderColor = 'var(--pink)'; sel.focus(); } toast('Elegí un talle primero'); return; }
    sel.style.borderColor = '';
    addToCart(id, sel.value);
  });

  /* fotos de la ficha de producto */
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-thumb]') : null;
    var main = $('pdpMain');
    if (!t || !main) return;
    main.src = assetUrl(t.getAttribute('data-thumb').replace(/^\//, ''));
    Array.prototype.forEach.call(document.querySelectorAll('.pdp-thumb'), function (b) { b.classList.toggle('active', b === t); });
  });

  /* clics en enlaces de WhatsApp (no del carrito) */
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[data-wa]') : null;
    if (!a) return;
    track('whatsapp_contacto');
    convert(CFG.ADS_LABEL_WHATSAPP);
  });

  /* ---------- menú móvil ---------- */
  var nav = $('mobileNav'), burger = $('hamburgerBtn');
  function closeNav() { if (nav) { nav.classList.remove('open'); if (burger) burger.setAttribute('aria-expanded', 'false'); } }
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- buscador del catálogo ---------- */
  var search = $('searchInput'), grid = $('productsGrid'), emptyMsg = $('emptyState');
  if (search && grid) {
    search.addEventListener('input', function () {
      var q = search.value.toLowerCase().trim(), shown = 0;
      Array.prototype.forEach.call(grid.querySelectorAll('.card-product'), function (c) {
        var ok = !q || (c.getAttribute('data-name') || '').indexOf(q) !== -1;
        c.hidden = !ok; if (ok) shown++;
      });
      if (emptyMsg) emptyMsg.hidden = shown !== 0;
    });
  }

  /* ---------- conversión por consulta enviada (página de gracias) ---------- */
  if (document.body.getAttribute('data-conversion') === 'lead') {
    var done = false;
    try { done = sessionStorage.getItem('ff_lead_sent') === '1'; sessionStorage.setItem('ff_lead_sent', '1'); } catch (e) {}
    if (!done) { track('generate_lead'); convert(CFG.ADS_LABEL_LEAD); }
  }

  /* acceso escondido al panel: 5 toques seguidos sobre el © del pie de página */
  var copy = $('copyAdmin');
  if (copy) {
    var taps = [];
    copy.addEventListener('click', function () {
      var now = Date.now();
      taps = taps.filter(function (t) { return now - t < 4000; }); taps.push(now);
      if (taps.length >= 5) { taps = []; window.location.href = pageUrl('admin/'); }
    });
  }

  saveCart();
  renderCart();
  if (removedMsg) { toast('Quitamos del carrito productos que ya no están disponibles'); }

  /* API para checkout.js */
  window.FF = {
    conf: CONF, byId: byId, money: money, pageUrl: pageUrl, assetUrl: assetUrl, preview: PREVIEW,
    cart: function () { return CART.slice(); }, clearCart: clearCart, totals: totals, count: count,
    waLink: waLink, orderLines: orderLines, track: track, convert: convert, cfg: CFG, maxQty: MAX_QTY
  };
})();
