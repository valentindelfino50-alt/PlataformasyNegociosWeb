/* Funny Foot: carrito, pedido por WhatsApp, búsqueda, menú y medición. */
(function () {
  'use strict';
  var CFG = window.FUNNYFOOT || {};
  var PRODUCTS = __PRODUCTS__;

  function money(n) { return '$' + Math.round(n).toLocaleString('es-AR'); }
  function byId(id) { for (var i = 0; i < PRODUCTS.length; i++) { if (PRODUCTS[i].id === id) return PRODUCTS[i]; } return null; }
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
  function convert(label) { try { if (window.gtag && CFG.ADS_ID && label) window.gtag('event', 'conversion', { send_to: CFG.ADS_ID + '/' + label }); } catch (e) {} }
  loadGoogleTag();

  /* ---------- carrito ---------- */
  var CART = [];
  try {
    var saved = JSON.parse(localStorage.getItem('funnyfoot_cart') || '[]');
    if (Array.isArray(saved)) {
      CART = saved.filter(function (i) { return i && byId(i.id) && i.size && i.qty > 0; })
        .map(function (i) { return { id: i.id, size: String(i.size).slice(0, 4), qty: Math.min(parseInt(i.qty, 10) || 1, 20) }; });
    }
  } catch (e) { CART = []; }
  function saveCart() { try { localStorage.setItem('funnyfoot_cart', JSON.stringify(CART)); } catch (e) {} }
  function total() { return CART.reduce(function (s, i) { return s + byId(i.id).price * i.qty; }, 0); }
  function count() { return CART.reduce(function (n, i) { return n + i.qty; }, 0); }

  function orderText() {
    var lines = ['Hola Funny Foot! Quiero hacer este pedido:', ''];
    CART.forEach(function (i) {
      var p = byId(i.id);
      lines.push('• ' + i.qty + ' x ' + p.name + ' (talle ' + i.size + ') - ' + money(p.price * i.qty));
    });
    lines.push('', 'Total de productos: ' + money(total()), '', 'Mi nombre:', 'Entrega (envío a domicilio o retiro en el local):');
    return lines.join('\n');
  }

  var toastTimer;
  function toast(msg) {
    var t = $('toast'); if (!t) return;
    $('toastMsg').textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('show'); }, 2200);
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
      var info = el('div', 'ci-info');
      info.appendChild(el('b', null, p.name));
      info.appendChild(el('span', null, 'Talle ' + item.size + ' · ' + money(p.price)));
      var r = el('div', 'ci-row');
      var step = el('div', 'qty-stepper');
      var minus = el('button', null, '−'); minus.type = 'button'; minus.setAttribute('aria-label', 'Quitar una unidad');
      minus.addEventListener('click', function () { changeQty(idx, -1); });
      var plus = el('button', null, '+'); plus.type = 'button'; plus.setAttribute('aria-label', 'Sumar una unidad');
      plus.addEventListener('click', function () { changeQty(idx, 1); });
      step.appendChild(minus); step.appendChild(el('span', null, String(item.qty))); step.appendChild(plus);
      var rm = el('button', 'ci-remove', 'Quitar'); rm.type = 'button';
      rm.addEventListener('click', function () { CART.splice(idx, 1); saveCart(); renderCart(); });
      r.appendChild(step); r.appendChild(rm);
      info.appendChild(r);
      row.appendChild(info);
      body.appendChild(row);
    });
    var rowT = el('div', 'row total');
    rowT.appendChild(el('span', null, 'Total de productos')); rowT.appendChild(el('span', null, money(total())));
    foot.appendChild(rowT);
    foot.appendChild(el('p', 'drawer-note', 'Enviás el pedido por WhatsApp y coordinamos disponibilidad, envío y pago. En este sitio no se cobra nada.'));
    var wa = el('a', 'btn btn-wa btn-block', 'Enviar pedido por WhatsApp');
    wa.id = 'waOrder';
    wa.target = '_blank'; wa.rel = 'noopener';
    wa.href = 'https://wa.me/' + encodeURIComponent(CFG.WHATSAPP || '') + '?text=' + encodeURIComponent(orderText());
    wa.addEventListener('click', function () {
      track('begin_checkout', { currency: 'ARS', value: total() });
      track('whatsapp_pedido', { value: total(), currency: 'ARS' });
      convert(CFG.ADS_LABEL_WHATSAPP);
    });
    foot.appendChild(wa);
  }
  function changeQty(idx, d) {
    CART[idx].qty += d;
    if (CART[idx].qty <= 0) CART.splice(idx, 1);
    if (CART[idx] && CART[idx].qty > 20) CART[idx].qty = 20;
    saveCart(); renderCart();
  }
  function addToCart(id, size) {
    var found = null;
    CART.forEach(function (i) { if (i.id === id && i.size === size) found = i; });
    if (found) found.qty = Math.min(found.qty + 1, 20); else CART.push({ id: id, size: size, qty: 1 });
    saveCart(); renderCart();
    var p = byId(id);
    track('add_to_cart', { currency: 'ARS', value: p.price, items: [{ item_id: String(p.id), item_name: p.name, price: p.price, quantity: 1 }] });
    toast('¡Agregado al pedido!');
  }

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

  /* botones "agregar" de las tarjetas */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('[data-add]') : null;
    if (!btn) return;
    var id = parseInt(btn.getAttribute('data-add'), 10);
    var sel = $('size-' + id);
    if (!sel || !sel.value) { if (sel) { sel.style.borderColor = 'var(--pink)'; sel.focus(); } toast('Elegí un talle primero'); return; }
    sel.style.borderColor = '';
    addToCart(id, sel.value);
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

  renderCart();
})();
