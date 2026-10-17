# Funny Foot: guía de publicación, panel de administración y compra

La carpeta **`funnyfoot-sitio/`** es el sitio completo. El resto del repositorio (esta guía, `netlify.toml`, `fuentes-del-sitio/`) no se publica.

## 1. Qué incluye

| Para qué | Qué hay |
|---|---|
| Tienda | Inicio, catálogo, páginas por categoría, ficha de cada producto con fotos, Nosotros, Contacto y políticas |
| Compra | Carrito, **Finalizar compra** (datos, envío o retiro, medio de pago), pedido registrado y página de confirmación con número de pedido |
| Administración | **Panel en `/admin/`**: productos (nombre, precio, talles, categoría, fotos, estado), categorías, datos del negocio, envíos y medios de pago |
| Google | `sitemap.xml`, `robots.txt`, datos estructurados de producto y local, medición de Analytics y Ads lista para activar |
| Formularios | Pedidos, contacto, suscripción y sugerencias, con Netlify Forms |

## 2. Cómo funciona (para entender qué se puede esperar)

1. El catálogo está en `funnyfoot-sitio/datos/productos.json` y las fotos en `funnyfoot-sitio/assets/productos/`.
2. El panel `/admin/` edita ese archivo y sube las fotos al repositorio de GitHub con **una sola publicación por vez**.
3. Netlify detecta el cambio, ejecuta `fuentes-del-sitio/build_site.py` (definido en `netlify.toml`), regenera las páginas y publica el sitio. Tarda 1 o 2 minutos.
4. Los pedidos llegan a Netlify Forms (panel **Forms → pedido**) y por email si activás el aviso.

No hay servidor propio ni base de datos. Es una tienda estática, por eso es rápida, barata y buena para Google.

## 3. Publicar en Netlify conectado a GitHub (≈ 10 minutos)

1. Entrá a [app.netlify.com](https://app.netlify.com) y registrate con **GitHub**.
2. Abrí [app.netlify.com/start](https://app.netlify.com/start), elegí **GitHub** y autorizá el acceso **solo a este repositorio**.
3. Elegí el repositorio y la rama `claude/fervent-ptolemy-r4iap9` (**Branch to deploy**).
4. Los campos de build ya vienen definidos en `netlify.toml`: comando `python3 fuentes-del-sitio/build_site.py` y carpeta `funnyfoot-sitio`. Dejalos como aparecen.
5. Poné un nombre de proyecto (por ejemplo `funnyfoot-caballito`) y tocá **Deploy**.
6. Si el deploy falla, abrí el registro del deploy en **Deploys** y mandáselo a Claude. La causa más probable es que no encuentre `python3`.
7. Entrá al panel (`/admin/`, ver sección 5) y en **Negocio y envíos** cargá la dirección real del sitio (`https://tu-nombre.netlify.app`) y publicá.

### Formularios
1. En Netlify abrí **Forms**: tienen que aparecer `pedido`, `contacto`, `suscripcion` y `sugerencias`.
2. Si no aparecen, activá **Form detection** en **Site configuration → Forms** y volvé a publicar.
3. En **Forms → Form notifications → Add notification → Email** configurá el aviso para `pedido` y `contacto`. Así te llega cada pedido por mail.
4. Para ver o exportar los mensajes: **Forms → (formulario) → Export CSV**.
5. Netlify limita los envíos de formularios por mes en el plan gratis. Revisá el límite vigente en su página de precios antes de empezar una campaña.

## 4. Completar los datos reales antes de anunciar

Google Ads exige datos del negocio reales y verificables. Hoy el sitio tiene los datos del diseño original: revisalos en el panel, en **Negocio y envíos**.

| Dato | Valor actual | Dónde se cambia |
|---|---|---|
| WhatsApp | `5491155550199` (parece de ejemplo) | Panel → Negocio y envíos |
| Teléfono, dirección y horarios | los del diseño original | Panel → Negocio y envíos |
| Envío gratis desde, costo de envío, descuento por transferencia, cuotas, plazos | $50.000 · $4.500 · 5% · 3 cuotas | Panel → Negocio y envíos |
| Datos bancarios (titular, CBU/CVU, alias) | vacío | Panel → Negocio y envíos |
| Fotos, precios, talles y descripciones | ilustraciones y precios del diseño | Panel → Productos |
| Razón social y CUIT (Defensa del Consumidor) | no están | Pedíselos a Claude, van en el pie de página |

**Si el número de WhatsApp no es real, el sitio no sirve para anunciar:** los pedidos y consultas no llegarían a nadie.

## 5. Panel de administración (`/admin/`)

### Para entrar
1. Creá un token en [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new).
2. En **Repository access** elegí **Only select repositories** y marcá el repositorio del sitio.
3. En **Permissions → Repository permissions** poné **Contents: Read and write**.
4. Elegí un vencimiento (por ejemplo 90 días), generá el token y pegalo en el panel.

El token se guarda **solo en el navegador** de quien lo usa y solo se envía a GitHub. **Quien tenga el token puede modificar el sitio**: no lo compartas ni lo dejes en computadoras ajenas. Para dar acceso a otra persona, agregala como colaboradora del repositorio y que cree su propio token.

### Qué se puede hacer
- **Productos:** crear, editar, duplicar y eliminar. Nombre, categoría, precio, talles (`23-28` o `23, 24, 26`), color, descripción, hasta 6 fotos (la primera es la principal), y las opciones *mostrar en la tienda*, *agotado*, *destacado en el inicio* y *luz LED*.
- **Fotos:** se eligen desde la computadora o el celular. Se redimensionan solas (máximo 1200 px) y se comprimen antes de subirlas.
- **Categorías:** crear, editar, ordenar y eliminar (si no tienen productos). Cada una tiene su propia página en el sitio.
- **Negocio y envíos:** datos de contacto, costos de envío, descuentos, medios de pago y datos para transferir.
- **Publicar:** muestra un resumen de los cambios y los sube de una vez. Si alguien publicó otra versión mientras editabas, avisa y no pisa nada.

### Qué conviene saber
- Cada publicación genera un deploy en Netlify. Cargá varios cambios y publicá una sola vez.
- Los cambios tardan 1 o 2 minutos en verse en el sitio.
- “Probar sin conectar” abre el panel con el catálogo actual para conocerlo; no guarda nada.

## 6. Cómo es la compra

1. **Carrito:** el cliente elige talle y agrega. Se limita a 10 unidades por modelo y talle. Los productos agotados u ocultos no se pueden comprar.
2. **Finalizar compra:** datos de contacto, envío a domicilio o retiro en el local, medio de pago y aceptación de términos. Muestra el total con envío y descuento, y valida cada campo.
3. **Pedido:** se envía a Netlify Forms con un número (`FF-AAMMDD-XXXX`), los productos, los totales y los datos del cliente. Si el envío falla, el cliente ve un aviso y puede mandar el pedido por WhatsApp; el reintento conserva el mismo número.
4. **Confirmación:** el cliente ve su número de pedido, el resumen y las instrucciones según el medio de pago (por ejemplo los datos para transferir). Tiene un botón para confirmar por WhatsApp con el número ya escrito.

### Lo que esta compra NO hace
- **No cobra en línea.** No hay pasarela de pago (Mercado Pago, tarjeta). El comercio contacta al cliente, confirma disponibilidad y acuerda el pago. Cobrar con tarjeta dentro del sitio requiere una cuenta de Mercado Pago y una función en Netlify con las credenciales: se puede agregar después.
- **No descuenta stock.** Si se agota un modelo, marcalo como *Agotado* en el panel.
- **Los precios los calcula el navegador del cliente.** Al recibir el pedido, verificá el total con los precios del panel. Es lo normal en una tienda con confirmación manual.

## 7. Google Ads (próximas 2 semanas)

El sitio no necesita aparecer en el buscador para anunciar: Google Ads revisa la página de destino de cada anuncio.

**Días 1 a 3: publicar y probar**
- [ ] Sitio publicado, con datos reales (sección 4) y la dirección del sitio cargada en el panel.
- [ ] En tu celular: ver un producto, agregarlo, finalizar la compra, comprobar que el pedido aparece en **Forms → pedido** y que llega el email.
- [ ] Abrí `/robots.txt` y `/sitemap.xml` de tu sitio para ver que respondan.

**Días 3 a 6: cuentas y medición**
- [ ] Creá la cuenta de **Google Ads** (con medio de pago) y una propiedad de **Google Analytics 4**.
- [ ] Copiá el ID de medición de GA4 (`G-XXXXXXXXXX`) y el de Google Ads (`AW-XXXXXXXXX`) en `funnyfoot-sitio/assets/js/config.js` (`GA4_ID` y `ADS_ID`). Pedile a Claude que lo cargue.
- [ ] En Google Ads creá tres conversiones y pegá la etiqueta de cada una en `config.js`:
  - **Compra** (`ADS_LABEL_COMPRA`): se dispara al confirmar un pedido, con el valor y el número de pedido.
  - **Consulta enviada** (`ADS_LABEL_LEAD`): se dispara al enviar el formulario de contacto.
  - **Clic en WhatsApp** (`ADS_LABEL_WHATSAPP`): se dispara al tocar un botón de WhatsApp.
- [ ] Comprobá con la extensión *Tag Assistant* de Google que las etiquetas se detecten.

**Días 6 a 10: campaña**
- [ ] Tipo: **Búsqueda**. Un grupo de anuncios por categoría, cada uno con su página de destino. Las URLs son `/productos/<categoría>/`; cada producto también tiene la suya en `/producto/<nombre>/`.
- [ ] Los textos de los anuncios deben coincidir con lo que muestra la página (precios, envíos, cuotas).

**Días 10 a 14: revisión y ajustes**
- Google revisa los anuncios en uno o varios días hábiles. Los motivos de rechazo más comunes: datos de contacto falsos, un destino que no funciona o promesas que la página no cumple.

**Opcional:** [Search Console](https://search.google.com/search-console) para aparecer sin pagar. Enviá `sitemap.xml`. Puede tardar días o semanas.

## 8. Vista previa en Claude

Mientras el sitio se define, la vista previa vive como artefacto de Claude. Es una copia del sitio con los enlaces ajustados a archivos: se regenera con `python3 fuentes-del-sitio/generar_vista_previa.py`.
En la vista previa el checkout no envía pedidos, los formularios solo muestran un aviso y el panel funciona únicamente en modo demostración.

## 9. Archivos del repositorio

```
funnyfoot-sitio/            ← lo que se publica
  datos/productos.json      ← catálogo y datos del negocio (lo edita el panel)
  assets/productos/         ← fotos subidas desde el panel
  assets/js/config.js       ← IDs de Google Analytics y Ads
  admin/                    ← panel de administración
netlify.toml                ← comando de build y carpeta publicada
fuentes-del-sitio/          ← generador de páginas y de la vista previa
GUIA-PUBLICACION.md         ← esta guía
```

Las páginas HTML, `sitemap.xml`, `robots.txt` y `assets/js/catalogo.js` se **generan**: no las edites a mano, se pisan en cada publicación. Para cambiar textos o diseño, pedíselo a Claude.
