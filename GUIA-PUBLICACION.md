# Funny Foot: guía de publicación, panel de administración y compra

La carpeta **`funnyfoot-sitio/`** es el sitio completo. El resto del repositorio (esta guía, `netlify.toml`, `fuentes-del-sitio/`) no se publica.

## 1. Qué incluye

| Para qué | Qué hay |
|---|---|
| Tienda | Inicio, catálogo, páginas por categoría, ficha de cada producto con fotos, Nosotros, Contacto y políticas |
| Compra | Carrito, **Finalizar compra** (datos, envío o retiro, medio de pago), pedido registrado y página de confirmación con número de pedido |
| Administración | **Panel en `/admin/`**: productos (nombre, precio, talles, categoría, fotos, estado), categorías, datos del negocio, envíos y medios de pago |
| Google | `sitemap.xml`, `robots.txt`, datos estructurados de producto y local, medición de Analytics y Ads lista para activar |
| Formularios | Pedidos, contacto y suscripción, con Netlify Forms |

## 2. Cómo funciona (para entender qué se puede esperar)

1. El catálogo está en `funnyfoot-sitio/datos/productos.json` y las fotos en `funnyfoot-sitio/assets/productos/`.
2. El panel `/admin/` edita ese archivo y sube las fotos al repositorio de GitHub, con **una sola publicación por vez**. Se entra con un usuario y un código; una función de Netlify (`netlify/functions/admin.js`) valida el acceso y publica con una clave guardada en secreto.
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
7. Configurá el acceso al panel (siguiente apartado, se hace una sola vez).
8. Entrá al panel (`/admin/`, ver sección 5) y en **Negocio y envíos** cargá la dirección real del sitio (`https://tu-nombre.netlify.app`) y publicá.

### Acceso al panel de administración (una sola vez)
El panel entra con el usuario **PlataformasyNegocios** y un código que vos elegís. El código y la clave de GitHub **no están en el sitio ni en el repositorio**: se guardan en las variables de entorno de Netlify.

1. Creá un token de GitHub en [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new):
   - **Repository access:** *Only select repositories* y marcá el repositorio del sitio.
   - **Permissions → Repository permissions → Contents:** *Read and write*.
   - Elegí un vencimiento (por ejemplo 1 año), generá el token y copialo.
2. En Netlify andá a **Project configuration → Environment variables → Add a variable** y cargá dos variables:

| Variable | Valor |
|---|---|
| `GITHUB_TOKEN` | el token que acabás de copiar |
| `ADMIN_CODE` | el código de ingreso que quieras (mínimo 8 caracteres, mejor 12 o más) |

3. En **Deploys → Trigger deploy → Deploy project** para que tome las variables.
4. Entrá a `https://tu-sitio/admin/`, con usuario `PlataformasyNegocios` y tu código.

Si al entrar ves **“El panel todavía no está configurado”**, el mensaje indica cuál de las dos variables no le llega a la función. Revisá que:
- el nombre sea exacto, en mayúsculas y sin espacios: `GITHUB_TOKEN` y `ADMIN_CODE`;
- el alcance (**Scopes**) incluya **Functions**;
- el código tenga al menos 8 caracteres;
- hayas publicado el sitio de nuevo **después** de crear las variables (las funciones toman las variables al publicar).

Variables opcionales: `ADMIN_USER` (cambia el usuario), `GITHUB_BRANCH` (si el sitio se publica desde otra rama) y `GITHUB_REPO`.

### Formularios
1. En Netlify abrí **Forms**: tienen que aparecer `pedido`, `contacto` y `suscripcion`.
2. Si no aparecen, activá **Form detection** en **Site configuration → Forms** y volvé a publicar.
3. En **Forms → Form notifications → Add notification → Email** configurá el aviso para `pedido` y `contacto`. Así te llega cada pedido por mail.
4. Para ver o exportar los mensajes: **Forms → (formulario) → Export CSV**. La suscripción solo guarda los emails: el sitio no envía newsletters por sí solo, los mails se mandan desde tu propia herramienta de correo.
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

### Cómo entrar
- Dirección: `https://tu-sitio/admin/`. No hay ningún botón visible en el sitio.
- Acceso escondido: tocá **5 veces seguidas el símbolo © del pie de página** y te lleva al panel.
- Usuario: `PlataformasyNegocios`. Código: el que definiste en `ADMIN_CODE`.
- La sesión dura hasta 12 horas. Podés tildar “Mantener la sesión abierta en este equipo” para no volver a escribir el código.
- Para dar acceso a otra persona alcanza con pasarle el usuario y el código. Para quitárselo, cambiá `ADMIN_CODE` en Netlify y volvé a publicar: todas las sesiones abiertas se cierran.

### Qué se puede hacer
- **Productos:** crear, editar, duplicar y eliminar. Nombre, categoría, precio, talles (`23-28` o `23, 24, 26`), color, descripción, hasta 6 fotos (la primera es la principal), y las opciones *mostrar en la tienda*, *agotado*, *destacado en el inicio* y *luz LED*.
- **Fotos:** se eligen desde la computadora o el celular. Se redimensionan solas (máximo 1200 px) y se comprimen antes de subirlas.
- **Categorías:** crear, editar, ordenar y eliminar (si no tienen productos). Cada una tiene su propia página en el sitio.
- **Negocio y envíos:** datos de contacto, costos de envío, descuentos, medios de pago y datos para transferir.
- **Publicar:** muestra un resumen de los cambios y los sube de una vez. Si alguien publicó otra versión mientras editabas, avisa y no pisa nada.

### Seguridad: qué tener en cuenta
- Quien tenga el usuario y el código puede cambiar productos, precios y datos de contacto (incluido el WhatsApp). Usá un código largo y no lo publiques.
- El servicio solo puede escribir `datos/productos.json` y fotos JPG dentro de `assets/productos/`. No puede tocar el código del sitio ni otros archivos.
- Un intento fallido de ingreso demora un poco la respuesta, pero no bloquea la cuenta: por eso conviene un código largo.
- Si el token de GitHub vence, el panel avisa “El token de GitHub configurado en Netlify no es válido o venció”. Generá uno nuevo y actualizá `GITHUB_TOKEN` en Netlify.
- Cada publicación genera un deploy en Netlify. Cargá varios cambios y publicá una sola vez. Los cambios tardan 1 o 2 minutos en verse.
- “Probar sin ingresar” abre el panel con el catálogo actual para conocerlo; no guarda nada.

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
netlify.toml                ← comando de build, carpeta publicada y carpeta de funciones
netlify/functions/admin.js  ← servicio del panel (valida usuario y código, publica en GitHub)
fuentes-del-sitio/          ← generador de páginas y de la vista previa
GUIA-PUBLICACION.md         ← esta guía
```

Las páginas HTML, `sitemap.xml`, `robots.txt` y `assets/js/catalogo.js` se **generan**: no las edites a mano, se pisan en cada publicación. Para cambiar textos o diseño, pedíselo a Claude.
