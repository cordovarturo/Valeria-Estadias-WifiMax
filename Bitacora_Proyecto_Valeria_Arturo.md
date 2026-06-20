# Bitácora Técnica del Proyecto Valeria — Asistente IA
## Wifimax ISP — Módulo de Desarrollo (Odoo + Node.js)

---

**Practicante:** Arturo Israel Martínez Córdova
**Matrícula:** 1224100528
**Institución:** UTNG (Universidad Tecnológica)
**Carrera:** TSU Desarrollo de Software
**Cuatrimestre:** 6to
**Rol en el proyecto:** Practicante de Desarrollo de Software (núcleo Odoo 18 + microservicio Node.js)
**Empresa:** Wifimax ISP, Dolores Hidalgo, Guanajuato
**Periodo que cubre este documento:** Semana 1-2 — Onboarding, planeación e instalación del entorno de desarrollo
**Fecha de elaboración:** 19-20 de junio de 2026

---

## ¿Qué es este documento?

Este documento tiene dos propósitos:

1. **Servir como reporte de avance** para mi institución, mostrando qué hice, cómo lo hice, y qué problemas resolví durante esta etapa del proyecto.
2. **Servir como guía técnica para mis compañeros de equipo**, explicando paso a paso cómo levanté el entorno de desarrollo desde cero, para que cualquiera de ellos pueda repetir el proceso en su propia computadora sin tener que descubrir todo por su cuenta.

Está escrito de forma detallada y sin asumir que quien lo lea ya sabe usar Docker u Odoo. Cada sección explica el "qué" y el "por qué", no solo el "cómo".

---

## 1. Contexto del proyecto

Wifimax ISP está desarrollando **Valeria**, una recepcionista virtual con inteligencia artificial que va a atender a los clientes de la empresa por WhatsApp y por llamada telefónica, las 24 horas del día. La idea es que el cliente nunca note que está hablando con una inteligencia artificial: Valeria debe sonar como una persona real, cálida y mexicana, que puede revisar el estado del servicio de un cliente, consultar saldos, recibir pagos, agendar visitas técnicas, y —cuando algo se complica— pasar la llamada a un agente humano con todo el contexto ya resuelto.

El proyecto se construye con dos piezas que trabajan juntas:

| Pieza | Para qué sirve |
|---|---|
| **Módulo de Odoo 18** (`wifimax_valeria`) | Aquí se guarda toda la información: las conversaciones, los clientes identificados, los tickets, los reportes. Es la parte "administrativa" que el equipo de Wifimax puede ver y revisar. |
| **Microservicio en Node.js** (se construye más adelante) | Aquí vive la parte de "tiempo real": recibe la llamada o el mensaje de WhatsApp, habla con la inteligencia artificial (Claude), genera la voz con ElevenLabs, y le pasa los datos importantes al módulo de Odoo. |

Mi rol específico dentro del equipo de 3 practicantes es el de **Desarrollo de Software**, encargado de construir ambas piezas. Mis dos compañeros de Redes y Telecomunicaciones se encargan de la telefonía (SIP Trunk, MikroTik) y del monitoreo de infraestructura (LibreNMS), respectivamente.

A continuación se muestra el diagrama de arquitectura completa que el equipo usó como referencia conceptual (incluye partes que no se construyen en este proyecto, como FreePBX, pero ilustra cómo se conectan los distintos sistemas de un ISP con IA):

![Arquitectura completa de referencia](images/01_arquitectura_completa.png)

---

## 2. ¿Qué se hizo en esta etapa (semana 1-2)?

Durante esta primera etapa, que correspondía a onboarding y planeación según el cronograma general del proyecto, el trabajo fue principalmente de **preparación**: no se tocó todavía la parte de telefonía ni de inteligencia artificial. El objetivo concreto que me tocó cumplir fue:

1. Instalar Docker en mi computadora.
2. Levantar Odoo 18 (versión Community, gratuita) en mi máquina, usando Docker.
3. Crear la primera versión del módulo `wifimax_valeria`, con un modelo de datos básico para guardar conversaciones.
4. Instalar ese módulo dentro de Odoo y comprobar que funciona, creando un registro de prueba.

Todo este trabajo se hizo en mi computadora personal (Linux, distribución Nobara), como un **entorno de desarrollo local**. Esto significa que nada de lo que se hizo aquí afecta los sistemas reales de Wifimax — es un espacio seguro para aprender, probar y cometer errores sin ningún riesgo.

---

## 3. Una nota importante sobre licencias de Odoo

Antes de empezar, vale la pena dejar registrado un punto de criterio técnico que tomé durante este proceso, porque puede ser útil para el resto del equipo.

En el grupo de trabajo se compartió un repositorio de GitHub que ofrecía una versión de "Odoo 18 Enterprise sin licencia". Decidí **no usar esa opción** y en su lugar instalar **Odoo 18 Community**, la versión oficial y gratuita que distribuye Odoo S.A. a través de Docker Hub.

La razón es sencilla: ese tipo de repositorios funcionan modificando el software para saltarse la verificación de la licencia de pago, lo cual es una violación de los términos de uso de Odoo, independientemente de las buenas intenciones con las que se use. Community cubre, sin ningún problema, todo lo que el módulo `wifimax_valeria` necesita: modelos de datos propios, vistas, permisos, conexión con clientes (`res.partner`), reportes, y comunicación por API. Si en algún punto futuro el proyecto necesitara específicamente un módulo exclusivo de Enterprise (por ejemplo, el de Suscripciones que se mencionó en el chat del equipo), esa sería una decisión que le corresponde tomar a la empresa, adquiriendo una licencia real — no algo que se resuelva con software modificado.

---

## 4. Requisitos previos (lo que cualquier compañero necesita tener)

Antes de seguir esta guía, cualquier persona del equipo necesita:

- Una computadora con Linux (esta guía se probó en **Nobara**, que está basada en Fedora; los comandos de instalación de Docker cambian un poco si usas Ubuntu/Debian — se indica más abajo)
- Conexión a internet (se descargan varios cientos de MB la primera vez)
- Acceso de administrador en su propia computadora (`sudo`)
- VS Code (o el editor de código de su preferencia) — no es obligatorio, pero esta guía usa VS Code como referencia visual

---

## 5. Paso 1 — Instalar Docker

**¿Qué es Docker y por qué lo usamos?** Docker permite tener un programa completo (en este caso, Odoo y su base de datos) corriendo en una especie de "caja" aislada dentro de la computadora, sin tener que instalar nada directamente en el sistema operativo. Esto evita conflictos entre programas y hace que todo el equipo trabaje exactamente con la misma versión, sin importar qué computadora use cada uno.

### Si usas Nobara o Fedora:

```bash
# 1. Quitar versiones viejas si existen (por ejemplo, si ya tenías Podman)
sudo dnf remove -y docker docker-client docker-client-latest docker-common \
  docker-latest docker-latest-logrotate docker-logrotate docker-engine \
  podman-docker

# 2. Instalar herramienta para manejar repositorios
sudo dnf -y install dnf-plugins-core

# 3. Agregar el repositorio oficial de Docker
sudo dnf config-manager addrepo --from-repofile=https://download.docker.com/linux/fedora/docker-ce.repo

# 4. Instalar Docker y sus complementos
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. Activar el servicio de Docker para que arranque siempre
sudo systemctl enable --now docker

# 6. Dar permiso a tu usuario para usar Docker sin escribir "sudo" cada vez
sudo usermod -aG docker $USER
```

### Si usas Ubuntu o Debian:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

### Paso clave que casi todos olvidan

Después del comando `usermod -aG docker $USER`, el cambio **no se aplica de inmediato**. Es necesario **cerrar sesión por completo y volver a entrar** (o reiniciar la computadora). Si no se hace esto, cualquier comando de Docker va a fallar con un error de "permission denied", como me pasó a mí (ver imagen de evidencia más abajo).

![Error de permisos antes de reiniciar sesión](images/03_terminal_permiso_denegado.png)

### Verificación de que Docker quedó bien instalado

Después de reiniciar sesión, se confirma que el usuario ya pertenece al grupo `docker`:

![Grupo docker confirmado en el usuario](images/07_groups_docker_confirmado.png)

Y se hace una prueba final descargando una imagen mínima de prueba:

```bash
docker run hello-world
```

Si todo salió bien, aparece un mensaje que empieza con **"Hello from Docker!"**. Esa es la confirmación oficial de que Docker funciona de punta a punta: pudo contactar al servidor de Docker, descargar una imagen de internet, y correr un programa dentro de un contenedor.

![Docker funcionando correctamente, instalado en Nobara](images/04_docker_instalado_nobara.png)

![Mensaje Hello from Docker confirmando instalación exitosa](images/05_hello_from_docker.png)

---

## 6. Paso 2 — Preparar la carpeta del proyecto

Se creó una carpeta de trabajo ordenada en la computadora, siguiendo la misma estructura que ya se había definido en el documento de planeación general del proyecto (carpeta `custom_addons` para los módulos propios de Odoo):

```bash
mkdir -p ~/wifimax-valeria/odoo
cd ~/wifimax-valeria/odoo
mkdir -p custom_addons config
```

Esto crea:

```
wifimax-valeria/
└── odoo/
    ├── custom_addons/    ← aquí van los módulos que nosotros programamos
    └── config/           ← aquí va el archivo de configuración de Odoo
```

![Estructura inicial de carpetas vista en VS Code](images/02_estructura_carpetas_vscode.png)

---

## 7. Paso 3 — El archivo que levanta todo: `docker-compose.yml`

Este archivo es el "plano de construcción" que le dice a Docker exactamente qué programas levantar y cómo deben conectarse entre sí. Se guarda en `~/wifimax-valeria/odoo/docker-compose.yml`.

```yaml
services:
  db:
    image: postgres:16
    container_name: wifimax_odoo_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - odoo_db_data:/var/lib/postgresql/data

  odoo:
    image: odoo:18
    container_name: wifimax_odoo
    restart: unless-stopped
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    volumes:
      - odoo_web_data:/var/lib/odoo
      - ./custom_addons:/mnt/extra-addons
      - ./config:/etc/odoo

volumes:
  odoo_db_data:
  odoo_web_data:
```

### Explicación en palabras simples

Este archivo describe **dos programas** que van a trabajar juntos:

- **`db`** es la base de datos (PostgreSQL), donde se guarda absolutamente toda la información de Odoo. Sin base de datos, Odoo no puede funcionar.
- **`odoo`** es el propio Odoo, la aplicación que vemos en el navegador.

Algunas líneas importantes de entender:

- **`image: odoo:18`** — le dice a Docker que descargue la versión oficial 18 de Odoo, publicada directamente por la empresa Odoo S.A. Es gratuita y legal.
- **`ports: "8069:8069"`** — abre la puerta para que podamos entrar a Odoo desde el navegador, en la dirección `http://localhost:8069`.
- **`./custom_addons:/mnt/extra-addons`** — esta línea es clave para todo el equipo: cualquier carpeta que pongamos dentro de `custom_addons` en nuestra computadora, automáticamente aparece dentro de Odoo. Aquí es donde vive nuestro módulo `wifimax_valeria`.
- **`./config:/etc/odoo`** — aquí va el archivo de configuración de Odoo, que se explica en el siguiente paso.

![Contenido final y verificado del docker-compose.yml](images/06_docker_compose_final.png)

---

## 8. Paso 4 — El archivo de configuración de Odoo

Dentro de la carpeta `config/`, se crea un archivo llamado **`odoo.conf`**. Sin este archivo, Odoo no sabe cómo conectarse a su propia base de datos y el programa se cae en un bucle de reinicios constantes (esto realmente pasó durante las pruebas, ver sección de problemas resueltos más abajo).

```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
data_dir = /var/lib/odoo
admin_passwd = admin123
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
```

**Explicación de cada línea:**

- `addons_path` — le dice a Odoo en qué carpetas debe buscar módulos. La segunda ruta (`/mnt/extra-addons`) es justamente donde está nuestro módulo `wifimax_valeria`.
- `admin_passwd` — esta es la contraseña "maestra" del servidor de Odoo, distinta de la contraseña del usuario administrador. Se usa para crear o eliminar bases de datos completas. **En este entorno de desarrollo es `admin123`.**
- `db_host`, `db_port`, `db_user`, `db_password` — son los datos para que Odoo se conecte a la base de datos PostgreSQL definida en el `docker-compose.yml`. **En este entorno de desarrollo, usuario y contraseña son ambos `odoo`.**

> **Nota de seguridad para todo el equipo:** estas contraseñas (`admin123` y `odoo`) son válidas únicamente para este entorno de desarrollo local, que vive solo en la computadora de cada practicante y no contiene ningún dato real de clientes de Wifimax. Cuando el proyecto avance a un servidor compartido del equipo o a producción, estas contraseñas deben cambiarse por unas mucho más seguras y no deben quedar escritas en ningún documento. Aquí se documentan tal cual para que cualquier compañero pueda levantar su propio entorno de prueba sin trabarse, no como práctica recomendada para producción.

---

## 9. Paso 5 — Levantar los contenedores

Con los dos archivos anteriores ya guardados, se levanta todo con un solo comando, ejecutado dentro de la carpeta `~/wifimax-valeria/odoo`:

```bash
docker compose up -d
```

La primera vez tarda varios minutos porque Docker tiene que descargar las imágenes de Odoo y PostgreSQL desde internet (varios cientos de MB). Las siguientes veces es casi instantáneo, porque ya las tiene guardadas.

Para confirmar que ambos servicios están corriendo:

```bash
docker compose ps
```

![Contenedores levantados exitosamente, ambos en estado Up](images/08_docker_compose_up_exitoso.png)

---

## 10. Problema real que se presentó y cómo se resolvió

Es importante documentar este problema porque seguramente cualquier otro compañero del equipo lo va a encontrar también.

**Síntoma:** Al entrar a `http://localhost:8069` en el navegador, aparecía el error `ERR_CONNECTION_REFUSED` (conexión rechazada). Al revisar el estado de los contenedores, Odoo aparecía en estado **`Restarting`** una y otra vez, en bucle.

**Diagnóstico:** Se revisaron los registros (logs) del contenedor con:

```bash
docker compose logs odoo
```

El mensaje de error decía:

```
grep: /etc/odoo/odoo.conf: No such file or directory
```

**Causa real:** En el `docker-compose.yml` se le había dicho a Odoo que su archivo de configuración estaría en `/etc/odoo/odoo.conf`, pero la carpeta `config/` en la computadora estaba completamente vacía — nunca se había creado el archivo `odoo.conf` dentro de ella.

**Solución:** Se creó el archivo `config/odoo.conf` con el contenido mostrado en la sección anterior, y se reiniciaron los contenedores:

```bash
docker compose down
docker compose up -d
```

Después de esto, el contenedor de Odoo quedó estable en estado `Up`, sin reiniciarse más.

![Contenedores estables después de la corrección, ya sin reinicios](images/09_docker_compose_down_up.png)

---

## 11. Paso 6 — Crear la base de datos de Odoo

Con Odoo ya corriendo, se entra desde el navegador a:

```
http://localhost:8069
```

La primera vez que se entra, Odoo no tiene ninguna base de datos creada, así que muestra el formulario de creación:

![Pantalla inicial de creación de base de datos](images/10_pantalla_master_password.png)

Los datos usados para este entorno de desarrollo fueron:

| Campo | Valor usado | Notas |
|---|---|---|
| **Master Password** | `admin123` | Coincide con `admin_passwd` del `odoo.conf` |
| **Database Name** | `wifimax_dev` | Nombre identificable como entorno de desarrollo |
| **Email** | `admin@wifimax.local` | Este será el usuario administrador de Odoo |
| **Password** | `Wifimax2026!` | Contraseña del usuario administrador |
| **Phone Number** | (opcional, se deja vacío o cualquier número) | No es obligatorio |
| **Language** | Español (MX) | Idioma de la interfaz |
| **Country** | México | |
| **Demo Data** | **Desmarcado** | Importante: así Odoo arranca limpio, sin datos de ejemplo que estorben al construir el módulo propio |

![Formulario lleno con los datos del entorno de desarrollo](images/11_formulario_lleno_demo_data.png)

> **Nota:** en la imagen anterior el checkbox de "Demo Data" aparece marcado en un punto intermedio del proceso; la recomendación final y la que se aplicó fue **desmarcarlo** antes de crear la base de datos, para no llenar Odoo con clientes y productos ficticios que no corresponden a Wifimax.

Después de darle clic en "Create database" y esperar a que Odoo termine de preparar todas sus tablas internas (puede tardar entre 30 y 60 segundos), se entra directo a la pantalla principal de Aplicaciones de Odoo, ya funcionando:

![Odoo funcionando con la pantalla de Aplicaciones](images/12_odoo_apps_creado.png)

Esto marcó el primer gran hito de esta etapa: **Odoo 18 Community corriendo completamente en un entorno local, de forma legal y reproducible por cualquier compañero del equipo.**

---

## 12. Paso 7 — Construcción del módulo `wifimax_valeria`

Con Odoo ya funcionando, el siguiente trabajo fue construir la primera versión del módulo propio donde se va a gestionar toda la información de Valeria. Un módulo de Odoo es, en esencia, una carpeta con una estructura específica de archivos que Odoo sabe cómo leer.

### Estructura final del módulo

```
custom_addons/
└── wifimax_valeria/
    ├── __init__.py                          ← le dice a Python qué cargar
    ├── __manifest__.py                      ← la "identidad" del módulo
    ├── models/
    │   ├── __init__.py                      ← le dice a Python qué modelo cargar
    │   └── valeria_conversation.py          ← aquí vive la información que se guarda
    ├── security/
    │   └── ir.model.access.csv              ← quién puede ver/editar esta información
    └── views/
        └── valeria_conversation_views.xml   ← cómo se ve en pantalla
```

### 12.1 — `__manifest__.py`: la identidad del módulo

Este archivo es obligatorio en cualquier módulo de Odoo. Es como su "acta de nacimiento": le dice al sistema el nombre del módulo, de qué otras partes de Odoo depende, y qué archivos debe leer.

```python
{
    'name': 'Wifimax Valeria - Asistente IA',
    'version': '18.0.1.0.0',
    'category': 'Customer Service',
    'summary': 'Gestión de conversaciones de Valeria, recepcionista virtual con IA',
    'description': """
Módulo de gestión para Valeria, la asistente de IA de Wifimax ISP.
Centraliza conversaciones (WhatsApp y llamadas), identificación de clientes,
tickets, escalaciones y reportes de desempeño.
    """,
    'author': 'Wifimax ISP',
    'website': 'https://wifimax.com',
    'license': 'LGPL-3',
    'depends': ['base', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/valeria_conversation_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

En palabras simples: `depends` indica que este módulo necesita que ya existan instaladas las partes básicas de Odoo (`base`), el sistema de contactos/clientes (`contacts`) y el sistema de mensajería interna (`mail`). La lista `data` indica qué otros archivos debe leer Odoo al instalar el módulo, y en qué orden.

![Archivo manifest creado y revisado en VS Code](images/13_manifest_creado.png)

### 12.2 — Los archivos `__init__.py`

Son archivos casi vacíos, pero esenciales: le indican a Python en qué carpetas debe buscar más código.

`wifimax_valeria/__init__.py`:
```python
from . import models
```

`wifimax_valeria/models/__init__.py`:
```python
from . import valeria_conversation
```

El primero dice "ve a la carpeta `models`"; el segundo dice "dentro de esa carpeta, carga el archivo `valeria_conversation.py`".

![Archivos correctamente ubicados después de corregir una confusión inicial de carpetas](images/14_manifest_movido_correcto.png)

### 12.3 — El modelo de datos: `models/valeria_conversation.py`

Aquí se define qué información se va a guardar por cada conversación que Valeria tenga con un cliente. Es la primera pieza real de "memoria" del sistema.

```python
# -*- coding: utf-8 -*-
from odoo import models, fields


class ValeriaConversation(models.Model):
    _name = 'wifimax.valeria.conversation'
    _description = 'Conversacion de Valeria con un cliente'
    _order = 'create_date desc'

    name = fields.Char(
        string='Referencia',
        required=True,
        default='Nueva conversacion',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
    )
    channel = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('call', 'Llamada telefonica'),
        ],
        string='Canal',
        required=True,
        default='call',
    )
    phone_number = fields.Char(
        string='Numero de telefono',
    )
    start_datetime = fields.Datetime(
        string='Inicio',
        default=fields.Datetime.now,
    )
    end_datetime = fields.Datetime(
        string='Fin',
    )
    resolved = fields.Boolean(
        string='Resuelta por Valeria',
        default=False,
    )
    escalated = fields.Boolean(
        string='Escalada a humano',
        default=False,
    )
    summary = fields.Text(
        string='Resumen de la conversacion',
    )
```

**¿Qué guarda cada campo, en palabras simples?**

| Campo | Qué guarda |
|---|---|
| `name` | Un nombre o referencia corta para identificar la conversación |
| `partner_id` | El cliente de Wifimax al que pertenece esta conversación (se conecta directo con la base de clientes que ya existe en Odoo) |
| `channel` | Si la conversación fue por WhatsApp o por llamada telefónica |
| `phone_number` | El número desde el que se comunicó el cliente |
| `start_datetime` / `end_datetime` | Cuándo empezó y cuándo terminó la conversación |
| `resolved` | Si Valeria logró resolver la consulta sola, sin ayuda humana |
| `escalated` | Si la conversación tuvo que pasarse a un agente humano |
| `summary` | Un resumen de lo que se habló, para que cualquier persona del equipo pueda entender rápido qué pasó |

### 12.4 — El archivo de permisos: `security/ir.model.access.csv`

Este archivo es obligatorio y, aunque parece poco importante, sin él Odoo bloquea por completo el acceso al modelo de datos por seguridad.

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_wifimax_valeria_conversation_user,wifimax.valeria.conversation.user,model_wifimax_valeria_conversation,base.group_user,1,1,1,1
```

En palabras simples, esta línea dice: *"cualquier usuario interno de Odoo (`base.group_user`) puede leer, escribir, crear y borrar registros de conversaciones de Valeria"* (los cuatro números `1` al final corresponden, en orden, a leer/escribir/crear/borrar).

![Archivo de permisos creado y verificado](images/15_security_csv_creado.png)

### 12.5 — La vista: `views/valeria_conversation_views.xml`

Este archivo define cómo se ve la información en pantalla: la tabla con la lista de conversaciones, el formulario para ver el detalle de una en particular, y el menú donde aparece todo esto dentro de Odoo.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_valeria_conversation_list" model="ir.ui.view">
        <field name="name">wifimax.valeria.conversation.list</field>
        <field name="model">wifimax.valeria.conversation</field>
        <field name="arch" type="xml">
            <list string="Conversaciones de Valeria">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="channel"/>
                <field name="start_datetime"/>
                <field name="resolved"/>
                <field name="escalated"/>
            </list>
        </field>
    </record>

    <record id="view_valeria_conversation_form" model="ir.ui.view">
        <field name="name">wifimax.valeria.conversation.form</field>
        <field name="model">wifimax.valeria.conversation</field>
        <field name="arch" type="xml">
            <form string="Conversación de Valeria">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="partner_id"/>
                        <field name="channel"/>
                        <field name="phone_number"/>
                        <field name="start_datetime"/>
                        <field name="end_datetime"/>
                        <field name="resolved"/>
                        <field name="escalated"/>
                        <field name="summary"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_valeria_conversation" model="ir.actions.act_window">
        <field name="name">Conversaciones de Valeria</field>
        <field name="res_model">wifimax.valeria.conversation</field>
        <field name="view_mode">list,form</field>
    </record>

    <menuitem id="menu_valeria_root"
              name="Valeria - Asistente IA"
              sequence="50"/>

    <menuitem id="menu_valeria_conversation"
              name="Conversaciones"
              parent="menu_valeria_root"
              action="action_valeria_conversation"
              sequence="1"/>

</odoo>
```

En palabras simples: este archivo crea, dentro de Odoo, un nuevo menú llamado **"Valeria - Asistente IA"** con un submenú **"Conversaciones"**, que muestra primero una tabla con todas las conversaciones registradas, y al hacer clic en alguna, abre un formulario con todo el detalle.

![Vista list y vista form definidas correctamente](images/16_views_xml_parte1.png)

![Continuación del archivo: acción y menús del módulo](images/17_views_xml_parte2.png)

---

## 13. Problema real número 2: error al instalar el módulo

Al intentar instalar el módulo por primera vez desde la pantalla de Aplicaciones de Odoo, apareció este error:

```
No se encontraron registros que coincidan con id externo
'model_wifimax_valeria_conversation' en el campo 'Model'
Missing required value for the field 'Model' (model_id)
```

**Diagnóstico:** este error significa que Odoo intentó cargar el archivo de permisos (`ir.model.access.csv`) **antes** de que el modelo de datos `wifimax.valeria.conversation` quedara registrado en el sistema. Se hicieron varias pruebas para descartar posibles causas:

- Se confirmó que el código de Python no tenía errores de sintaxis.
- Se confirmó que los archivos `__init__.py` estaban correctos.
- Se confirmó, usando la consola interactiva de Odoo (`odoo shell`), que el modelo sí se podía importar correctamente cuando Odoo cargaba todo su entorno real.

**Causa real encontrada:** al revisar el estado del módulo directamente en la base de datos, se confirmó que estaba marcado como `uninstalled` (nunca instalado). El comando que se había usado para forzar la actualización por terminal usaba la bandera `-u` (actualizar), pero esa bandera solo funciona en módulos que **ya están instalados**. Para un módulo nuevo, hay que usar `-i` (instalar).

**Solución aplicada:**

```bash
docker compose exec odoo odoo -d wifimax_dev -i wifimax_valeria --stop-after-init
```

Con este comando, Odoo sí reconoció e instaló el módulo correctamente, sin ningún error, registrando el modelo de datos primero y los permisos después, en el orden correcto.

![Módulo visible en Aplicaciones de Odoo](images/18_modulo_visible_apps.png)

![Confirmación del módulo Wifimax Valeria listado en Aplicaciones](images/19_modulo_visible_apps2.png)

Después de esta instalación exitosa por terminal, se reinició el contenedor de Odoo para que la interfaz web reflejara el cambio:

![Reinicio del contenedor de Odoo](images/20_restart_odoo.png)

![Aplicaciones mostrando el módulo ya instalado, sin botón de Activar](images/21_aplicaciones_instalado.png)

![Confirmación final del módulo instalado correctamente](images/22_modulo_instalado_final.png)

---

## 14. Resultado final: primer registro de prueba

Con el módulo ya instalado, se entró al nuevo menú **"Valeria - Asistente IA" → "Conversaciones"**, se creó un registro de prueba llamado **"Prueba 1"**, seleccionando el canal **"Llamada telefónica"**, y se guardó exitosamente.

Esto confirma que el ciclo completo funciona de principio a fin:

```
Código en Python (modelo)
        ↓
Permisos (quién puede usarlo)
        ↓
Vista (cómo se ve en pantalla)
        ↓
Instalación dentro de Odoo
        ↓
Creación de un registro real
```

Este es exactamente el primer ladrillo de lo que más adelante va a recibir información real, generada automáticamente cuando Valeria conteste una llamada o un mensaje de WhatsApp de un cliente real de Wifimax.

---

## 15. Guía rápida para que cualquier compañero replique este entorno

Esta sección resume, sin tanta explicación, los pasos exactos para que otro miembro del equipo levante el mismo entorno en su propia computadora.

```bash
# 1. Instalar Docker (ver sección 5 según tu distribución de Linux)
# 2. Reiniciar sesión después de agregar tu usuario al grupo docker

# 3. Crear la carpeta del proyecto
mkdir -p ~/wifimax-valeria/odoo
cd ~/wifimax-valeria/odoo
mkdir -p custom_addons config

# 4. Crear el archivo docker-compose.yml (contenido en sección 7)

# 5. Crear el archivo config/odoo.conf (contenido en sección 8)

# 6. Levantar los contenedores
docker compose up -d

# 7. Esperar unos segundos y entrar a http://localhost:8069
#    Crear base de datos con Demo Data DESMARCADO

# 8. Copiar la carpeta custom_addons/wifimax_valeria desde el repositorio
#    del equipo (o pedirla directamente a Arturo)

# 9. Instalar el módulo (la primera vez SIEMPRE con -i, no con -u)
docker compose exec odoo odoo -d <nombre_de_tu_base_de_datos> -i wifimax_valeria --stop-after-init

# 10. Reiniciar Odoo y entrar a Aplicaciones para confirmar que aparece
docker compose restart odoo
```

### Credenciales del entorno de desarrollo local (no usar en producción)

| Servicio | Usuario | Contraseña | Dónde se define |
|---|---|---|---|
| Base de datos PostgreSQL | `odoo` | `odoo` | `docker-compose.yml` |
| Master Password de Odoo (administración de bases de datos) | — | `admin123` | `config/odoo.conf` |
| Usuario administrador de Odoo (dentro de la base `wifimax_dev`) | `admin@wifimax.local` | `Wifimax2026!` | Se define al crear la base de datos |

---

## 16. Próximos pasos (lo que sigue según el cronograma del proyecto)

Según la planeación general de 16 semanas del proyecto Valeria, lo que sigue después de esta etapa es:

- Agregar el modelo `wifimax.valeria.message`, para guardar cada mensaje individual dentro de una conversación (no solo el resumen general).
- Empezar el scaffold del microservicio en Node.js, que es la pieza que eventualmente va a recibir llamadas reales a través de Twilio.
- Conectar una cuenta de prueba de Twilio y lograr la primera llamada de prueba que conteste con un saludo simple.

---

## 17. Reflexión personal sobre esta etapa

Aunque el avance técnico de estas dos semanas se centró en la preparación del entorno y no todavía en la inteligencia artificial o la telefonía, este proceso fue valioso porque me obligó a entender a fondo cómo funciona Odoo por dentro: cómo se relacionan los archivos de un módulo, por qué el orden de carga importa, y cómo diagnosticar un error leyendo los registros del sistema en vez de adivinar.

Los dos problemas reales que se presentaron (el contenedor reiniciándose en bucle por falta del archivo de configuración, y el error de instalación por usar la bandera incorrecta) terminaron siendo las partes más útiles del aprendizaje, porque representan exactamente el tipo de obstáculos que cualquier desarrollador encuentra al trabajar con un sistema como Odoo por primera vez.
