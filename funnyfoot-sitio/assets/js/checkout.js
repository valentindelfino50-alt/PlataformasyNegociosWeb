/* Funny Foot: finalizar compra (checkout) y página de pedido recibido.
   El pedido se registra con Netlify Forms (formulario "pedido") y se muestra el resumen con las instrucciones de pago. */
(function () {
  'use strict';
  var FF = window.FF;
  if (!FF) return;
  var CONF = FF.conf;
  var LAST_KEY = 'ff_ultimo_pedido';

  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function checked(name) { var r = document.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ''; }
  function payName(v) {
    var m = (CONF.metodosPago || []).filter(function (x) { return x.id === v; })[0];
    return m ? m.nombre : v;
  }
  function itemsOf(cart) {
    return cart.map(function (i) {
      var p = FF.byId(i.id);
      return { id: p.id, nombre: p.nombre, talle: i.size, cantidad: i.qty, precio: p.precio, imagen: p.imagen || '', color: p.color || '' };
    });
  }
  function lineText(it) { return it.cantidad + ' × ' + it.nombre + ' — talle ' + it.talle + ' — ' + FF.money(it.precio * it.cantidad); }
  function itemRow(it) {
    var row = el('div', 'co-item');
    var thumb = el('div', 'co-thumb');
    if (it.imagen) { var img = el('img'); img.src = FF.assetUrl(it.imagen); img.alt = ''; thumb.appendChild(img); }
    else {
      var ns = 'http://www.w3.org/2000/svg';
      var svg = document.createElementNS(ns, 'svg'); svg.setAttribute('viewBox', '0 0 120 80'); svg.style.color = it.color || '#ED0B6F';
      var use = document.createElementNS(ns, 'use'); use.setAttribute('href', '#ic-sneaker'); svg.appendChild(use); thumb.appendChild(svg);
    }
    var info = el('div', 'co-item-info');
    info.appendChild(el('b', null, it.nombre));
    info.appendChild(el('span', null, 'Talle ' + it.talle + ' · ' + it.cantidad + ' x ' + FF.money(it.precio)));
    row.appendChild(thumb); row.appendChild(info); row.appendChild(el('b', null, FF.money(it.precio * it.cantidad)));
    return row;
  }
  function newOrderNumber() {
    var d = new Date();
    var ymd = String(d.getFullYear()).slice(2) + ('0' + (d.getMonth() + 1)).slice(-2) + ('0' + d.getDate()).slice(-2);
    var r = '';
    var chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    for (var i = 0; i < 4; i++) { r += chars.charAt(Math.floor(Math.random() * chars.length)); }
    return 'FF-' + ymd + '-' + r;
  }
  /* Mensaje que llega escrito al chat de WhatsApp del comercio. */
  function orderMessage(o) {
    var cierre = {
      transferencia: CONF.datosTransferencia ? 'Voy a transferir y te mando el comprobante por acá. ¡Gracias! 😊' : '¿Me pasan los datos para transferir? ¡Gracias! 😊',
      mercadopago: '¿Me pasan el link de Mercado Pago para pagar? ¡Gracias! 😊',
      tarjeta: '¿Me pasan el link para pagar con tarjeta? ¡Gracias! 😊',
      efectivo: 'Pago en efectivo cuando lo retire. ¡Gracias! 😊'
    }[o.pago] || '¿Coordinamos el pago? ¡Gracias! 😊';
    var L = ['¡Hola ' + (CONF.nombre || 'Funny Foot') + '! 👋 Quiero confirmar mi pedido *' + o.numero + '* de la web:', '', '🛍️ *Mi pedido*'];
    o.items.forEach(function (it) { L.push('• ' + lineText(it)); });
    L.push('', '💰 *Total: ' + FF.money(o.total) + '* (' + payName(o.pago) + ')',
      o.entrega === 'retiro' ? '🏬 Lo retiro en el local' : '📦 Envío a: ' + o.direccion,
      '👤 A nombre de: ' + o.nombre);
    if (o.telefono) L.push('📞 Mi teléfono: ' + o.telefono);
    L.push('', cierre);
    return L.join('\n');
  }

  /* ======================= CHECKOUT ======================= */
  function initCheckout(form) {
    var cart = FF.cart();
    if (!cart.length) { $('coEmpty').hidden = false; $('coGrid').hidden = true; return; }
    FF.track('begin_checkout', { currency: 'ARS', value: FF.totals('domicilio', '').subtotal });

    var numero = newOrderNumber();
    var busy = false;
    var domBlock = $('domBlock');
    var itemsBox = $('coItems');

    var domDesc = $('entregaDomDesc');
    if (CONF.envioGratisDesde && CONF.costoEnvio) domDesc.textContent = 'Gratis desde ' + FF.money(CONF.envioGratisDesde) + ' · si no, ' + FF.money(CONF.costoEnvio);
    else if (CONF.costoEnvio) domDesc.textContent = FF.money(CONF.costoEnvio);
    else domDesc.textContent = 'Sin cargo';

    function render() {
      var entrega = checked('entrega');
      var pago = checked('pago');
      domBlock.hidden = entrega === 'retiro';
      Array.prototype.forEach.call(document.querySelectorAll('[data-solo-retiro]'), function (opt) {
        var input = opt.querySelector('input');
        var off = entrega !== 'retiro';
        input.disabled = off;
        opt.classList.toggle('disabled', off);
      });
      var cur = document.querySelector('input[name="pago"]:checked');
      if (!cur || cur.disabled) {
        var first = document.querySelector('input[name="pago"]:not(:disabled)');
        if (first) { first.checked = true; pago = first.value; }
      }
      var t = FF.totals(entrega, pago);
      itemsBox.textContent = '';
      itemsOf(FF.cart()).forEach(function (it) { itemsBox.appendChild(itemRow(it)); });
      $('sSubtotal').textContent = FF.money(t.subtotal);
      $('sDescRow').hidden = !t.descuento;
      if (t.descuento) { $('sDescLabel').textContent = 'Descuento por transferencia (' + CONF.descuentoTransferencia + '%)'; $('sDesc').textContent = '−' + FF.money(t.descuento); }
      $('sEnvio').textContent = entrega === 'retiro' ? 'Retiro en el local · Sin cargo' : (t.envio === 0 ? 'Gratis' : FF.money(t.envio));
      $('sTotal').textContent = FF.money(t.total);
    }
    form.addEventListener('change', function (e) { if (e.target.name === 'entrega' || e.target.name === 'pago') render(); });
    render();
    $('fNumero').value = numero;

    /* ---- validación ---- */
    function setErr(name, msg) {
      var p = form.querySelector('[data-err="' + name + '"]');
      var input = form.querySelector('[name="' + name + '"]');
      if (p) { p.textContent = msg || ''; p.hidden = !msg; }
      if (input && input.type !== 'radio') { if (msg) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid'); }
      return msg;
    }
    function validate() {
      var v = function (name) { var f = form.elements[name]; return f ? String(f.value || '').trim() : ''; };
      var entrega = checked('entrega');
      var errs = [];
      var phoneDigits = v('telefono').replace(/\D/g, '');
      var checks = [
        ['nombre', v('nombre').length < 3 ? 'Ingresá tu nombre y apellido.' : ''],
        ['email', !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v('email')) ? 'Ingresá un email válido.' : ''],
        ['telefono', (phoneDigits.length < 8 || phoneDigits.length > 15) ? 'Ingresá un teléfono válido (con característica).' : '']
      ];
      if (entrega === 'domicilio') {
        checks.push(['direccion', v('direccion').length < 5 ? 'Ingresá calle y número.' : '']);
        checks.push(['localidad', v('localidad').length < 2 ? 'Ingresá tu localidad.' : '']);
        checks.push(['cp', !/^[A-Za-z]?\d{4}[A-Za-z]{0,3}$/.test(v('cp')) ? 'Ingresá un código postal válido (4 números).' : '']);
      } else {
        ['direccion', 'localidad', 'cp'].forEach(function (n) { setErr(n, ''); });
      }
      checks.push(['acepta', !form.elements.acepta.checked ? 'Tenés que aceptar los términos para continuar.' : '']);
      checks.push(['pago', !document.querySelector('input[name="pago"]:checked') ? 'Elegí un medio de pago.' : '']);
      checks.forEach(function (c) { if (setErr(c[0], c[1])) errs.push(c[0]); });
      return errs;
    }
    form.addEventListener('input', function (e) { if (e.target.name) setErr(e.target.name, ''); });

    /* ---- envío del pedido ---- */
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy) return;
      var cartNow = FF.cart();
      if (!cartNow.length) { $('coEmpty').hidden = false; $('coGrid').hidden = true; return; }
      var errs = validate();
      if (errs.length) {
        var first = form.querySelector('[name="' + errs[0] + '"]');
        if (first) { first.focus(); first.scrollIntoView({ block: 'center' }); }
        return;
      }
      var entrega = checked('entrega'), pago = checked('pago');
      var t = FF.totals(entrega, pago);
      var items = itemsOf(cartNow);
      var f = form.elements;
      var direccion = entrega === 'retiro' ? '' : [f.direccion.value.trim() + (f.piso.value.trim() ? ' (' + f.piso.value.trim() + ')' : ''), f.localidad.value.trim(), f.provincia.value, 'CP ' + f.cp.value.trim().toUpperCase()].join(', ');
      f.productos.value = items.map(lineText).join('\n');
      f.productos_json.value = JSON.stringify(items.map(function (i) { return { id: i.id, nombre: i.nombre, talle: i.talle, cantidad: i.cantidad, precio: i.precio }; }));
      f.subtotal.value = t.subtotal; f.descuento.value = t.descuento; f.envio.value = t.envio; f.total.value = t.total;
      f.pedido_numero.value = numero;

      var order = {
        numero: numero, fecha: new Date().toISOString(), nombre: f.nombre.value.trim(), email: f.email.value.trim(),
        telefono: f.telefono.value.trim(), entrega: entrega, direccion: direccion, pago: pago, items: items,
        subtotal: t.subtotal, descuento: t.descuento, envio: t.envio, total: t.total, preview: FF.preview
      };

      busy = true;
      var btn = $('coSubmit'); btn.disabled = true; btn.textContent = 'Enviando pedido…';
      var body = new URLSearchParams(new FormData(form)).toString();
      var send;
      if (FF.preview) send = Promise.resolve();   /* en la vista previa de Claude no hay dónde enviar el formulario */
      else send = postOrder(body).catch(function () { return new Promise(function (r) { setTimeout(r, 600); }).then(function () { return postOrder(body); }); });
      /* El cliente siempre llega a la confirmación: si el registro automático falló, el pedido viaja por WhatsApp. */
      function finish(sent) {
        order.sent = sent;
        if (!sent) order.body = body;
        try { localStorage.setItem(LAST_KEY, JSON.stringify(order)); } catch (err) {}
        FF.clearCart();
        window.location.href = FF.pageUrl('pedido-recibido/');
      }
      send.then(function () { finish(true); }, function (err) {
        try { console.warn('[Funny Foot] No se pudo registrar el pedido en Netlify Forms:', err && err.message); } catch (e2) {}
        finish(false);
      });
    });
  }

  /* envía el pedido a Netlify Forms (formulario "pedido") */
  function postOrder(body) {
    var ctl = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 10000);
    return fetch(FF.pageUrl(''), {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body, signal: ctl ? ctl.signal : undefined
    }).then(function (res) { clearTimeout(timer); if (!res.ok) throw new Error('HTTP ' + res.status); },
      function (err) { clearTimeout(timer); throw err; });
  }

  /* ======================= PEDIDO RECIBIDO ======================= */
  function copyText(text, btn) {
    function ok() { var t = btn.textContent; btn.textContent = '¡Copiado!'; setTimeout(function () { btn.textContent = t; }, 1800); }
    if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(ok, function () {}); return; }
    var ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta);
    ta.select(); try { document.execCommand('copy'); ok(); } catch (e) {} document.body.removeChild(ta);
  }

  function initRecibido() {
    var o = null;
    try { o = JSON.parse(localStorage.getItem(LAST_KEY) || 'null'); } catch (e) { o = null; }
    if (!o || !o.numero || !Array.isArray(o.items)) { $('oVacio').hidden = false; return; }
    $('pedidoOk').hidden = false;
    $('oNumero').textContent = o.numero;
    function aviso() {
      $('oAviso').textContent = o.preview ? 'Vista previa: este pedido de prueba no se envió a nadie.'
        : (o.sent ? 'Ya registramos tu pedido. Para confirmarlo más rápido, mandanos el mensaje por WhatsApp: ya está escrito.'
          : 'Tu pedido está listo. Para confirmarlo, enviánoslo por WhatsApp con el botón verde: el mensaje ya está escrito.');
    }
    aviso();
    /* si el registro automático había fallado, se reintenta en segundo plano sin molestar al cliente */
    if (!o.sent && !o.preview && o.body) {
      postOrder(o.body).then(function () {
        o.sent = true; delete o.body;
        try { localStorage.setItem(LAST_KEY, JSON.stringify(o)); } catch (e) {}
        aviso();
      }, function () {});
    }
    var box = $('oItems'); box.textContent = '';
    o.items.forEach(function (it) { box.appendChild(itemRow(it)); });
    $('oSubtotal').textContent = FF.money(o.subtotal);
    $('oDescRow').hidden = !o.descuento;
    if (o.descuento) $('oDesc').textContent = '−' + FF.money(o.descuento);
    $('oEnvio').textContent = o.entrega === 'retiro' ? 'Retiro en el local · Sin cargo' : (o.envio === 0 ? 'Gratis' : FF.money(o.envio));
    $('oTotal').textContent = FF.money(o.total);
    $('oEntrega').textContent = o.entrega === 'retiro' ? 'Retirás en: ' + (CONF.direccion || 'nuestro local') + '. ' + (CONF.horarios || '') : 'Enviamos a: ' + o.direccion;

    var datos = (CONF.datosTransferencia || '').trim();
    var pago = $('oPago'); pago.textContent = '';
    var waTxt = 'Tocá el botón y se abre el chat con tu pedido ya escrito. Solo tenés que enviarlo.';
    if (o.pago === 'transferencia') {
      pago.appendChild(el('h2', null, 'Datos para transferir'));
      if (datos) {
        pago.appendChild(el('p', null, 'Transferí ' + FF.money(o.total) + ' e indicá el pedido ' + o.numero + ' como referencia.'));
        pago.appendChild(el('pre', 'bank', datos));
        var cp = el('button', 'btn btn-outline btn-sm', 'Copiar datos'); cp.type = 'button';
        cp.addEventListener('click', function () { copyText(datos, cp); });
        pago.appendChild(cp);
        pago.appendChild(el('p', 'note-small', 'Después enviános el comprobante por WhatsApp para dejar el pedido confirmado.'));
        waTxt = 'Cuando hagas la transferencia, mandanos el comprobante por este chat. Tu pedido ya queda escrito.';
      } else {
        pago.appendChild(el('p', null, 'Te pasamos los datos bancarios por WhatsApp apenas nos escribas.'));
        waTxt = 'Tocá el botón y escribinos: te pasamos los datos para transferir ' + FF.money(o.total) + '.';
      }
    } else {
      pago.appendChild(el('h2', null, 'Cómo seguimos: ' + payName(o.pago)));
      pago.appendChild(el('p', null, {
        mercadopago: 'Te enviamos el link de Mercado Pago por WhatsApp para que pagues ' + FF.money(o.total) + '.',
        tarjeta: 'Te enviamos por WhatsApp un link seguro para pagar con tarjeta.',
        efectivo: 'Pagás ' + FF.money(o.total) + ' en efectivo en el local, cuando retirás tu pedido.'
      }[o.pago] || 'Te contactamos para acordar el pago.'));
    }
    $('oWaTexto').textContent = waTxt;
    var wa = $('oWa'); wa.href = FF.waLink(orderMessage(o));
    wa.addEventListener('click', function () { if (!o.preview) { FF.track('whatsapp_pedido', { value: o.total, currency: 'ARS' }); FF.convert((FF.cfg || {}).ADS_LABEL_WHATSAPP); } });

    /* copia del resumen al correo del propio cliente (se abre su app de correo) */
    if (o.email) {
      var plain = orderMessage(o).replace(/\*/g, '') + (o.pago === 'transferencia' && datos ? '\n\nDatos para transferir:\n' + datos : '');
      var mail = $('oMail');
      mail.href = 'mailto:' + encodeURIComponent(o.email) + '?subject=' + encodeURIComponent('Mi pedido ' + o.numero + ' en ' + (CONF.nombre || 'Funny Foot')) + '&body=' + encodeURIComponent(plain);
      mail.hidden = false;
    }

    var key = 'ff_compra_' + o.numero, already = false;
    try { already = sessionStorage.getItem(key) === '1'; sessionStorage.setItem(key, '1'); } catch (e) {}
    if (!already && !o.preview) {
      FF.track('purchase', {
        transaction_id: o.numero, value: o.total, currency: 'ARS', shipping: o.envio,
        items: o.items.map(function (i) { return { item_id: String(i.id), item_name: i.nombre, price: i.precio, quantity: i.cantidad }; })
      });
      FF.convert((FF.cfg || {}).ADS_LABEL_COMPRA, { value: o.total, currency: 'ARS', transaction_id: o.numero });
    }
  }

  var form = $('checkoutForm');
  if (form) initCheckout(form);
  else if ($('pedidoOk')) initRecibido();
})();
