# Funny Foot: guía para publicar en Netlify y salir con Google Ads

La carpeta **`funnyfoot-sitio/`** es el sitio completo. También está comprimida en **`funnyfoot-sitio.zip`**.
Todo lo que está fuera de esa carpeta (esta guía, `reemplazar.js`, `fuentes-del-sitio/`) **no se publica**.

## 1. Qué tiene el sitio

| Para qué | Qué incluye |
|---|---|
| Páginas reales (cada una con su dirección, título y descripción para Google) | Inicio, Productos, 4 categorías, Nosotros, Contacto, Envíos y pagos, Cambios y devoluciones, Privacidad y términos |
| Pedidos | Carrito que arma el pedido y lo envía por **WhatsApp**. El sitio no cobra ni simula compras |
| Formularios | Contacto, suscripción y sugerencias, con Netlify Forms (sin servidor propio) |
| Google | `sitemap.xml`, `robots.txt`, datos estructurados del local, medición lista para activar |
| Navegación | Funciona en celular y escritorio, modo claro y oscuro |

Qué se cambió respecto del artefacto de Claude, y por qué:
- **Se quitó el checkout simulado** (confirmación de compra con número de pedido falso). Google Ads puede rechazar sitios que aparentan cobrar sin hacerlo.
- **Se quitó el aviso "sitio demostrativo, no procesa pagos reales"** y se reemplazó por una explicación real: los pedidos se coordinan por WhatsApp.
- **Se quitaron los testimonios** y la frase "+40 modelos", porque no se pueden comprobar. Si son opiniones reales de clientes, se pueden volver a poner.
- **Se quitaron los íconos de Instagram y Facebook**, que apuntaban a las portadas genéricas de esas redes.
- **Se quitó "y mujeres"** de los textos, porque el catálogo solo tiene calzado infantil.

## 2. Completá esto ANTES de publicar (obligatorio para Google Ads)

Google Ads exige que los datos del negocio sean reales y verificables. Hoy el sitio tiene los datos del artefacto original.
Revisá cada uno. Si alguno no es real, cambialo.

| Dato | Valor actual | Cómo cambiarlo |
|---|---|---|
| WhatsApp (se ve en pantalla y en los datos para Google) | `11 5555-0199` | `node reemplazar.js "11 5555-0199" "11 XXXX-XXXX"` |
| WhatsApp (en los enlaces) | `5491155550199` | `node reemplazar.js "5491155550199" "54911XXXXXXXX"` |
| Dirección | `Av. Rivadavia 6521` | `node reemplazar.js "Av. Rivadavia 6521" "tu dirección"` |
| Horarios | `Lunes a viernes 10 a 19h · Sábados 10 a 14h` | igual que arriba |

**El número `5555-0199` parece un número de ejemplo.** Si no es el real, los anuncios no sirven: los pedidos no llegan a ningún lado.

Confirmá también que sean ciertos los textos de las políticas: envío gratis desde $50.000 y $4.500 de costo fijo, 3 cuotas sin interés, 5% de descuento por transferencia, 30 días para cambios, convenios con colegios de Caballito, retiro en el local.
Para cambiarlos, editá `envios-y-pagos/index.html`, `cambios-y-devoluciones/index.html` y `nosotros/index.html`.

Además:
- **Precios y talles**: están en `fuentes-del-sitio/build_site.py` (lista `PRODUCTS`) y también en los archivos HTML. Si cambiás precios, avisame y regenero el sitio completo.
- **Fotos**: hoy cada producto muestra una ilustración. Cuando tengas fotos reales, se agregan. Las necesitás para anuncios de Shopping.
- **Razón social, CUIT y email**: la normativa de Defensa del Consumidor los pide visibles. Agregalos en el pie de página con:
  `node reemplazar.js "© 2026 Funny Foot Calzados. Todos los derechos reservados." "© 2026 Funny Foot Calzados · Razón social … · CUIT … · email … · Todos los derechos reservados."`

## 3. Publicar en Netlify (≈ 10 minutos)

1. Creá una cuenta gratis en [netlify.com](https://www.netlify.com) (podés entrar con tu cuenta de Google).
2. Entrá a [app.netlify.com/drop](https://app.netlify.com/drop) y arrastrá la carpeta `funnyfoot-sitio` (o el `.zip`).
3. Netlify te da una dirección tipo `nombre-raro.netlify.app`. Entrá a **Site configuration → Change site name** y elegí un nombre propio, por ejemplo `funnyfoot-caballito`. Tu dirección final será `https://funnyfoot-caballito.netlify.app`.
4. **Reemplazá la dirección de ejemplo en todo el sitio** (afecta al sitemap, `robots.txt`, canonical y vista previa al compartir):
   `node reemplazar.js "SU-SITIO.netlify.app" "funnyfoot-caballito.netlify.app"`
5. Volvé a arrastrar la carpeta `funnyfoot-sitio` sobre tu sitio, en la pestaña **Deploys**, para publicar los cambios.
6. Si publicaste sin reclamar el sitio con tu cuenta, Netlify puede dar de baja el sitio a las 24 horas. Reclamalo desde la cuenta ya creada.

### Formularios
1. En Netlify entrá a **Forms**. Tienen que aparecer `contacto`, `suscripcion` y `sugerencias`.
2. Si no aparecen, andá a **Site configuration → Forms** y activá **Form detection**. Después volvé a publicar.
3. Configurá el aviso por email en **Forms → Form notifications → Add notification → Email notification**. Así te llega cada consulta.
4. Para leer todos los mensajes: **Forms → (formulario) → Export CSV**. Podés pegarlos en el chat y los organizo.
5. El plan gratis de Netlify tiene un límite mensual de envíos de formularios. Verificá el límite vigente en su página de precios antes de la campaña, porque puede cambiar.

## 4. Google Ads: pasos para las próximas 2 semanas

El sitio no necesita aparecer en el buscador para anunciar. Google Ads revisa la página de destino de cada anuncio.

**Días 1 a 3: publicar y probar**
- [ ] Sitio publicado, con datos reales (sección 2) y dirección final cargada (sección 3).
- [ ] Probá en tu celular: ver productos, agregar al pedido, enviar el pedido por WhatsApp, enviar el formulario de contacto y comprobar que llega el email.
- [ ] Abrí `https://tu-sitio/robots.txt` y `https://tu-sitio/sitemap.xml` para ver que respondan.

**Días 3 a 6: cuentas y medición**
- [ ] Creá la cuenta de **Google Ads** (con medio de pago) y una propiedad de **Google Analytics 4**.
- [ ] Copiá el ID de medición de GA4 (`G-XXXXXXXXXX`) y el ID de Google Ads (`AW-XXXXXXXXX`) en `funnyfoot-sitio/assets/js/config.js`, en `GA4_ID` y `ADS_ID`.
- [ ] En Google Ads creá dos conversiones. Pegá la **etiqueta** de cada una en `config.js`:
  - **Consulta enviada** (`ADS_LABEL_LEAD`): se dispara al llegar a `/gracias/`, después de enviar el formulario de contacto.
  - **Pedido por WhatsApp** (`ADS_LABEL_WHATSAPP`): se dispara al tocar "Enviar pedido por WhatsApp" o cualquier botón de WhatsApp.
- [ ] Volvé a publicar y comprobá con la extensión *Tag Assistant* de Google que las etiquetas se detecten.

**Días 6 a 10: campaña**
- [ ] Tipo de campaña: **Búsqueda**. Un grupo de anuncios por categoría, cada uno con su página de destino:

| Grupo de anuncios | Página de destino |
|---|---|
| Zapatillas con luz LED | `/productos/zapatillas-con-luz-led/` |
| Botas y botitas | `/productos/botas-y-botitas/` |
| Zapatillas urbanas | `/productos/zapatillas-urbanas/` |
| Zapatillas deportivas | `/productos/zapatillas-deportivas/` |
| Marca y local | `/` |

- [ ] Segmentá por ubicación (CABA/GBA o todo el país, según lo que vayas a enviar) y por idioma (español).
- [ ] Los textos de los anuncios deben coincidir con la página: no prometas precios, descuentos o cuotas que el sitio no muestre.
- [ ] Pedime las palabras clave y los textos de anuncios cuando llegues a este paso.

**Días 10 a 14: revisión y ajustes**
- Google revisa los anuncios, normalmente entre uno y varios días hábiles. Si rechaza alguno, el motivo aparece en la columna *Estado*.
- Los motivos más comunes: datos de contacto falsos, destino que no funciona, o promesas que la página no cumple.

**Opcional: aparecer en Google sin pagar**
En [Search Console](https://search.google.com/search-console) agregá tu sitio por URL, verificalo y enviá `sitemap.xml`. Puede tardar días o semanas y no hay garantía. No hace falta para anunciar.

## 5. Cosas a tener en cuenta

- **El sitio es estático.** Cualquier cambio de textos, precios o productos se hace editando los archivos y volviendo a publicar. Si me pasás los cambios, regenero toda la carpeta.
- **Los mensajes de "Sugerencias" llegan a Netlify, no al chat de Claude.** Exportalos en CSV y pegalos acá para que los analicemos.
- **Si es un trabajo práctico con un negocio ficticio**, Google Ads no es el lugar para probarlo con dinero real. Consultá con tu profesor si la campaña puede ser simulada.
- **No hay aviso de cookies.** La ley argentina de datos personales (25.326) no lo exige tal como el reglamento europeo, pero la política de privacidad ya describe el uso de etiquetas de Google. Si vas a anunciar a usuarios de la Unión Europea, habría que sumar un aviso.

## 6. Archivos del repositorio

```
funnyfoot-sitio/        ← lo que se publica
funnyfoot-sitio.zip     ← lo mismo, comprimido
GUIA-PUBLICACION.md     ← esta guía
reemplazar.js           ← cambia un texto en todo el sitio (necesita Node.js)
fuentes-del-sitio/      ← generador del sitio, para regenerarlo si cambian los productos
```
