'use strict';
/*
 * Función de Netlify del panel de administración (/admin/).
 *
 * El navegador manda usuario y código; esta función los valida y, si son correctos, publica en GitHub con una
 * clave que vive SOLO en las variables de entorno de Netlify (nunca en el sitio ni en el repositorio).
 *
 * Variables de entorno (Netlify → Project configuration → Environment variables):
 *   ADMIN_CODE     (obligatoria) código de ingreso, mínimo 8 caracteres
 *   GITHUB_TOKEN   (obligatoria) token de GitHub con permiso "Contents: Read and write" sobre el repositorio
 *   ADMIN_USER     (opcional)    usuario, por defecto "PlataformasyNegocios"
 *   GITHUB_REPO    (opcional)    por defecto "valentindelfino50-alt/PlataformasyNegociosWeb"
 *   GITHUB_BRANCH  (opcional)    por defecto "claude/fervent-ptolemy-r4iap9"
 *   SITE_DIR       (opcional)    carpeta del sitio en el repositorio, por defecto "funnyfoot-sitio"
 *
 * Solo permite escribir datos/productos.json y fotos .jpg en assets/productos/.
 */
const crypto = require('crypto');

const SESSION_HOURS = 12;
const MAX_BODY = 5.5 * 1024 * 1024;
const IMG_REL = /^assets\/productos\/[a-z0-9._-]{1,80}\.jpg$/;
const DATA_REL = 'datos/productos.json';

function cfg() {
  const e = process.env;
  return {
    token: e.GITHUB_TOKEN || '',
    code: e.ADMIN_CODE || '',
    user: e.ADMIN_USER || 'PlataformasyNegocios',
    repo: e.GITHUB_REPO || 'valentindelfino50-alt/PlataformasyNegociosWeb',
    branch: e.GITHUB_BRANCH || 'claude/fervent-ptolemy-r4iap9',
    dir: (e.SITE_DIR || 'funnyfoot-sitio').replace(/^\/+|\/+$/g, '')
  };
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function reply(status, obj) {
  return { statusCode: status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }, body: JSON.stringify(obj) };
}
function fail(status, error, message) { const e = new Error(message); e.status = status; e.code = error; return e; }

function sha256(s) { return crypto.createHash('sha256').update(s).digest(); }
function safeEqual(a, b) { return crypto.timingSafeEqual(sha256(String(a)), sha256(String(b))); }
function secret(c) { return sha256('ff-admin|' + c.code + '|' + c.token).toString('hex'); }
function sign(c, exp) { return exp.toString(36) + '.' + crypto.createHmac('sha256', secret(c)).update(String(exp)).digest('hex'); }
function verify(c, token) {
  const m = /^([a-z0-9]+)\.([a-f0-9]{64})$/.exec(String(token || ''));
  if (!m) return false;
  const exp = parseInt(m[1], 36);
  if (!(exp > Date.now())) return false;
  return safeEqual(sign(c, exp), token);
}

async function gh(c, method, path, body) {
  const res = await fetch('https://api.github.com/repos/' + c.repo + path, {
    method,
    headers: Object.assign({
      'Authorization': 'Bearer ' + c.token, 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'funnyfoot-admin'
    }, body ? { 'Content-Type': 'application/json' } : {}),
    body: body ? JSON.stringify(body) : undefined
  });
  let json = {};
  try { json = await res.json(); } catch (e) { json = {}; }
  if (!res.ok) {
    const e = new Error(json.message || ('GitHub respondió ' + res.status)); e.status = res.status; e.github = true; throw e;
  }
  return json;
}
const enc = (s) => s.split('/').map(encodeURIComponent).join('/');

async function readData(c) {
  const f = await gh(c, 'GET', '/contents/' + enc(c.dir + '/' + DATA_REL) + '?ref=' + encodeURIComponent(c.branch));
  return { text: Buffer.from(String(f.content).replace(/\s/g, ''), 'base64').toString('utf8'), sha: f.sha };
}

/* Comprobaciones mínimas del catálogo antes de aceptar un archivo de datos. */
function checkCatalog(text) {
  let d;
  try { d = JSON.parse(text); } catch (e) { throw fail(400, 'datos', 'El catálogo no es un JSON válido.'); }
  if (!d || typeof d !== 'object' || !d.negocio || !d.tienda || !Array.isArray(d.categorias) || !Array.isArray(d.productos)) throw fail(400, 'datos', 'Al catálogo le faltan secciones.');
  if (d.productos.length > 400 || d.categorias.length > 60) throw fail(400, 'datos', 'El catálogo es demasiado grande.');
  if (!/^\d{10,15}$/.test(String(d.negocio.whatsapp || ''))) throw fail(400, 'datos', 'El WhatsApp debe tener entre 10 y 15 números.');
  d.productos.forEach((p) => {
    if (typeof p.id !== 'number' || typeof p.nombre !== 'string' || typeof p.precio !== 'number') throw fail(400, 'datos', 'Hay un producto con datos inválidos.');
    (p.imagenes || []).forEach((i) => { if (!IMG_REL.test(i)) throw fail(400, 'datos', 'Hay una foto con una ruta no permitida.'); });
  });
}

async function handle(event) {
  if (event.httpMethod !== 'POST') throw fail(405, 'metodo', 'Método no permitido.');
  const raw = event.isBase64Encoded ? Buffer.from(event.body || '', 'base64').toString('utf8') : (event.body || '');
  if (raw.length > MAX_BODY) throw fail(413, 'tamano', 'El envío es demasiado grande.');
  let req;
  try { req = JSON.parse(raw || '{}'); } catch (e) { throw fail(400, 'json', 'Pedido inválido.'); }
  const c = cfg();

  if (!c.code || c.code.length < 8 || !c.token) {
    throw fail(503, 'config', 'El panel todavía no está configurado en Netlify: faltan las variables ADMIN_CODE (mínimo 8 caracteres) y GITHUB_TOKEN.');
  }

  if (req.action === 'login') {
    const okUser = safeEqual(String(req.usuario || '').trim().toLowerCase(), c.user.toLowerCase());
    const okCode = safeEqual(String(req.codigo || ''), c.code);
    if (!(okUser && okCode)) { await sleep(1200); throw fail(401, 'credenciales', 'Usuario o código incorrectos.'); }
    const exp = Date.now() + SESSION_HOURS * 3600 * 1000;
    return { token: sign(c, exp), expira: exp };
  }

  const auth = (event.headers && (event.headers.authorization || event.headers.Authorization)) || '';
  if (!verify(c, auth.replace(/^Bearer\s+/i, ''))) throw fail(401, 'sesion', 'La sesión venció. Volvé a entrar.');

  if (req.action === 'load') return readData(c);

  if (req.action === 'blob') {
    if (req.kind === 'datos') {
      if (typeof req.text !== 'string' || req.text.length > 1.5 * 1024 * 1024) throw fail(400, 'datos', 'Datos inválidos.');
      checkCatalog(req.text);
      return { sha: (await gh(c, 'POST', '/git/blobs', { content: req.text, encoding: 'utf-8' })).sha };
    }
    if (req.kind === 'foto') {
      const buf = Buffer.from(String(req.base64 || ''), 'base64');
      if (buf.length < 100 || buf.length > 3 * 1024 * 1024) throw fail(400, 'foto', 'La foto es muy grande o está vacía.');
      if (!(buf[0] === 0xFF && buf[1] === 0xD8 && buf[2] === 0xFF)) throw fail(400, 'foto', 'La foto tiene que ser un JPG.');
      return { sha: (await gh(c, 'POST', '/git/blobs', { content: buf.toString('base64'), encoding: 'base64' })).sha };
    }
    throw fail(400, 'blob', 'Tipo de archivo no permitido.');
  }

  if (req.action === 'commit') {
    const entries = Array.isArray(req.entries) ? req.entries : [];
    if (!entries.length || entries.length > 120) throw fail(400, 'commit', 'No hay cambios para publicar.');
    const tree = entries.map((e) => {
      const okPath = e.path === DATA_REL || IMG_REL.test(String(e.path));
      if (!okPath) throw fail(400, 'ruta', 'Ruta no permitida: ' + String(e.path).slice(0, 60));
      if (e.sha === null) { if (e.path === DATA_REL) throw fail(400, 'ruta', 'No se puede borrar el catálogo.'); return { path: c.dir + '/' + e.path, mode: '100644', type: 'blob', sha: null }; }
      if (!/^[a-f0-9]{40}$/.test(String(e.sha))) throw fail(400, 'sha', 'Archivo inválido.');
      return { path: c.dir + '/' + e.path, mode: '100644', type: 'blob', sha: e.sha };
    });
    const current = await readData(c);
    if (current.sha !== String(req.baseSha || '')) throw fail(409, 'conflicto', 'Se publicó otra versión del catálogo mientras editabas. Recargá el panel para traer los últimos cambios.');
    const ref = await gh(c, 'GET', '/git/ref/heads/' + enc(c.branch));
    const parent = ref.object.sha;
    const commit = await gh(c, 'GET', '/git/commits/' + parent);
    const newTree = await gh(c, 'POST', '/git/trees', { base_tree: commit.tree.sha, tree });
    const message = 'Panel: ' + String(req.message || 'Actualizar el catálogo').replace(/[\r\n]+/g, ' ').slice(0, 180);
    const nc = await gh(c, 'POST', '/git/commits', { message, tree: newTree.sha, parents: [parent] });
    await gh(c, 'PATCH', '/git/refs/heads/' + enc(c.branch), { sha: nc.sha, force: false });
    const data = entries.filter((e) => e.path === DATA_REL)[0];
    return { sha: nc.sha, url: nc.html_url || ('https://github.com/' + c.repo + '/commit/' + nc.sha), jsonSha: data ? data.sha : null };
  }

  throw fail(400, 'accion', 'Acción desconocida.');
}

exports.handler = async function (event) {
  try {
    return reply(200, await handle(event));
  } catch (e) {
    if (e.github) {
      // los detalles de GitHub no se muestran tal cual: pueden incluir datos del repositorio o del token
      const map = { 401: 'El token de GitHub configurado en Netlify no es válido o venció.', 403: 'El token de GitHub no tiene permiso de escritura sobre el repositorio.', 404: 'No se encontró el repositorio, la rama o el archivo del catálogo en GitHub.', 409: 'Hubo un conflicto con la versión publicada. Recargá el panel.', 422: 'Hubo un conflicto con la versión publicada. Recargá el panel.' };
      return reply(502, { error: 'github', message: map[e.status] || 'GitHub no pudo completar la operación.' });
    }
    return reply(e.status || 500, { error: e.code || 'error', message: e.status ? e.message : 'Error inesperado del servidor.' });
  }
};
// para pruebas
exports._internal = { cfg, sign, verify };
