#!/usr/bin/env node
/*
  Reemplaza un texto en TODOS los archivos de la carpeta funnyfoot-sitio.
  Uso:   node reemplazar.js "texto viejo" "texto nuevo"
  Ejemplo: node reemplazar.js "SU-SITIO.netlify.app" "funnyfoot-caballito.netlify.app"
*/
const fs = require('fs');
const path = require('path');
const [, , viejo, nuevo] = process.argv;
if (!viejo || nuevo === undefined) {
  console.log('Uso: node reemplazar.js "texto viejo" "texto nuevo"');
  process.exit(1);
}
const raiz = path.join(__dirname, 'funnyfoot-sitio');
const ext = new Set(['.html', '.js', '.css', '.xml', '.txt', '.json', '.webmanifest', '.svg']);
let archivos = 0, cambios = 0;
(function recorrer(dir) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) { recorrer(p); continue; }
    if (!ext.has(path.extname(f)) && f !== '_headers') continue;
    const txt = fs.readFileSync(p, 'utf8');
    const n = txt.split(viejo).length - 1;
    if (n > 0) { fs.writeFileSync(p, txt.split(viejo).join(nuevo)); archivos++; cambios += n; }
  }
})(raiz);
console.log(`Listo: ${cambios} reemplazos en ${archivos} archivos.`);
