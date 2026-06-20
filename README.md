# Wifimax Valeria — Asistente IA

Recepcionista virtual con inteligencia artificial para Wifimax ISP. Atiende a los clientes por WhatsApp y llamada telefónica, identifica al cliente, consulta su servicio, genera pagos, agenda visitas técnicas y escala a un agente humano cuando es necesario — todo sin que el cliente note que está hablando con una IA.

> **Proyecto de estadía — Wifimax ISP, Dolores Hidalgo, Gto.**
> Equipo: 3 practicantes TSU (1 Desarrollo de Software + 2 Redes y Telecomunicaciones)

---

## Tabla de contenido

- [¿Qué es Valeria?](#qué-es-valeria)
- [Arquitectura](#arquitectura)
- [Estado actual del proyecto](#estado-actual-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Instalación del entorno de desarrollo](#instalación-del-entorno-de-desarrollo)
- [Credenciales del entorno local](#credenciales-del-entorno-local)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Cómo instalar el módulo de Odoo](#cómo-instalar-el-módulo-de-odoo)
- [Comandos útiles del día a día](#comandos-útiles-del-día-a-día)
- [Problemas comunes y solución](#problemas-comunes-y-solución)
- [Roles del equipo](#roles-del-equipo)
- [Roadmap](#roadmap)
- [Licencias y uso de software](#licencias-y-uso-de-software)

---

## ¿Qué es Valeria?

Valeria es una recepcionista virtual que atiende a todos los suscriptores de Wifimax las 24 horas del día, los 365 días del año, por WhatsApp Business y llamadas telefónicas. Se comporta como una agente humana real — el cliente nunca sabe que está hablando con una IA — con voz femenina mexicana natural y respuesta en menos de 1 segundo.

**Capacidades principales:**

- Consultar saldo y vencimiento del servicio
- Revisar el estado del servicio (ONU activa, corte en zona, falla local)
- Generar referencias de pago (SPEI/CoDi vía OpenPay)
- Abrir tickets de soporte automáticamente
- Agendar visitas técnicas
- Escalar a un agente humano con el contexto completo, cuando lo amerite

**Reglas de comportamiento (resumen):**

| ✓ SIEMPRE | ✗ NUNCA |
|---|---|
| Saludar como persona | Decir "soy una IA" |
| Confirmar acciones antes de ejecutarlas | Admitir que es un robot |
| Resumir al final lo que se resolvió | Compartir datos de un cliente con otro |
| Decir "un momento" mientras consulta datos | Quedarse en silencio más de 2 segundos |

---

## Arquitectura

El sistema se construye con dos piezas que trabajan en conjunto:

```
┌─────────────────────────┐         ┌──────────────────────────┐
│   MÓDULO ODOO 18         │  JSON-RPC │  MICROSERVICIO Node.js   │
│   wifimax_valeria         │◄────────►│                            │
│                            │         │                            │
│  • Clientes / contratos    │         │  • Twilio ConversationRelay│
│  • Conversaciones          │         │  • Claude API (cerebro)    │
│  • Tickets                 │         │  • ElevenLabs (voz)        │
│  • Reportes                │         │  • WhatsApp Business API   │
│  • Configuración           │         │  • OpenPay / MikroTik      │
└─────────────────────────┘         └──────────────────────────┘
              │                                    │
              └──────────────┬─────────────────────┘
                              ▼
                    PostgreSQL (compartida)
```

- **Odoo 18** centraliza la gestión: clientes, historial, tickets, reportes — todo visible para el equipo de Wifimax en la interfaz que ya conocen.
- **Microservicio Node.js** (aún no construido) maneja todo lo de tiempo real: la llamada en vivo, la conversación con la IA, la síntesis de voz.

---

## Estado actual del proyecto

>  **Fase: Onboarding / Fundación — Semana 1-2 de 16**

| Componente | Estado |
|---|---|
| Entorno Docker + Odoo 18 Community local | ✅ Funcionando |
| Módulo `wifimax_valeria` — scaffold inicial | ✅ Instalado y probado |
| Modelo `wifimax.valeria.conversation` | ✅ Creado, con registro de prueba |
| Modelo `wifimax.valeria.message` | ⬜ Pendiente |
| Microservicio Node.js | ⬜ Pendiente |
| Integración Twilio | ⬜ Pendiente |
| Integración Claude API | ⬜ Pendiente |
| Integración ElevenLabs | ⬜ Pendiente |
| Integración WhatsApp Business | ⬜ Pendiente |
| Integración OpenPay | ⬜ Pendiente |
| Conector MikroTik | ⬜ Pendiente (a cargo de Redes #1) |
| Conector LibreNMS | ⬜ Pendiente (a cargo de Redes #2) |

Bitácora técnica detallada de esta etapa, con explicación paso a paso y capturas: [`docs/Bitacora_Proyecto_Valeria_Arturo.md`](docs/Bitacora_Proyecto_Valeria_Arturo.md)

---

## Requisitos previos

Para levantar el entorno de desarrollo en tu propia máquina necesitas:

- Linux (probado en Nobara/Fedora; también funciona en Ubuntu/Debian)
- [Docker](https://docs.docker.com/engine/install/) y Docker Compose v2
- Git
- VS Code (opcional, pero recomendado)
- ~2 GB de espacio libre (imágenes de Odoo + PostgreSQL)

---

## Instalación del entorno de desarrollo

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd <nombre_del_repo>
```

### 2. Instalar Docker (si no lo tienes)

<details>
<summary><b>Nobara / Fedora</b></summary>

```bash
sudo dnf remove -y docker docker-client docker-client-latest docker-common \
  docker-latest docker-latest-logrotate docker-logrotate docker-engine podman-docker

sudo dnf -y install dnf-plugins-core
sudo dnf config-manager addrepo --from-repofile=https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```
</details>

<details>
<summary><b>Ubuntu / Debian</b></summary>

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```
</details>

>  **Importante:** después de `usermod -aG docker $USER`, **cierra sesión por completo y vuelve a entrar** (o reinicia tu PC). Si no lo haces, todos los comandos `docker` van a fallar con `permission denied`.

Verifica que quedó bien instalado:

```bash
docker run hello-world
```

Debe mostrar un mensaje que empieza con `Hello from Docker!`.

### 3. Levantar Odoo + PostgreSQL

```bash
cd odoo
docker compose up -d
docker compose ps
```

Espera a que ambos contenedores (`wifimax_odoo` y `wifimax_odoo_db`) queden en estado `Up`.

### 4. Crear la base de datos

Abre el navegador en:

```
http://localhost:8069
```

Llena el formulario de creación con los datos de la siguiente sección. **Deja "Demo Data" desmarcado.**

---

## Credenciales del entorno local

>  Estas credenciales son válidas **únicamente para el entorno de desarrollo local** de cada practicante (no contienen datos reales de clientes de Wifimax). Si en algún momento se despliega un servidor compartido del equipo o de producción, estas contraseñas deben cambiarse y **no deben quedar documentadas en texto plano**.

| Dato | Valor |
|---|---|
| **URL de Odoo** | `http://localhost:8069` |
| **Puerto de Odoo** | `8069` |
| **Master Password** (administración de bases de datos) | `admin123` |
| **Nombre de base de datos sugerido** | `wifimax_dev` |
| **Usuario administrador de Odoo** | `admin@wifimax.local` |
| **Contraseña del administrador** | `Wifimax2026!` |
| **Usuario de PostgreSQL** | `odoo` |
| **Contraseña de PostgreSQL** | `odoo` |
| **Puerto de PostgreSQL** (interno, dentro de la red de Docker) | `5432` |

Estos valores están definidos en `odoo/docker-compose.yml` y `odoo/config/odoo.conf` — si los cambias ahí, cambian en todos lados.

---

## Estructura del repositorio

```
.
├── README.md
├── docs/
│   └── Bitacora_Proyecto_Valeria_Arturo.md   # bitácora detallada paso a paso
└── odoo/
    ├── docker-compose.yml      # levanta Odoo 18 + PostgreSQL 16
    ├── config/
    │   └── odoo.conf           # configuración de Odoo (puertos, addons_path, credenciales)
    └── custom_addons/
        └── wifimax_valeria/    # módulo propio de Odoo
            ├── __init__.py
            ├── __manifest__.py
            ├── models/
            │   ├── __init__.py
            │   └── valeria_conversation.py
            ├── security/
            │   └── ir.model.access.csv
            └── views/
                └── valeria_conversation_views.xml
```

### `docker-compose.yml`

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

### `config/odoo.conf`

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

---

## Cómo instalar el módulo de Odoo

>  **Para un módulo nuevo, usa siempre `-i` (install), nunca `-u` (update).** Usar `-u` en un módulo que nunca se ha instalado no hace nada — Odoo lo ignora silenciosamente. Este fue uno de los problemas reales documentados en la bitácora.

### Opción A — Desde la terminal (recomendada, más confiable)

```bash
docker compose exec odoo odoo -d wifimax_dev -i wifimax_valeria --stop-after-init
docker compose restart odoo
```

### Opción B — Desde la interfaz web

1. Activa el modo desarrollador: **Ajustes → Activar el modo desarrollador**
2. Ve a **Aplicaciones → Actualizar lista de aplicaciones**
3. Busca `Wifimax Valeria`
4. Clic en **Activar**

Después de instalar, el menú **"Valeria - Asistente IA"** aparece en la barra superior, con el submenú **"Conversaciones"**.

---

## Comandos útiles del día a día

```bash
# Levantar los contenedores
docker compose up -d

# Ver el estado de los contenedores
docker compose ps

# Ver los logs de Odoo en vivo
docker compose logs -f odoo

# Ver los últimos 100 logs sin quedarte "pegado"
docker compose logs odoo --tail=100

# Reiniciar solo Odoo (después de cambiar código del módulo)
docker compose restart odoo

# Apagar todo
docker compose down

# Apagar y BORRAR los volúmenes (borra la base de datos completa, usar con cuidado)
docker compose down -v

# Entrar a la consola interactiva de Odoo (para probar código Python directo)
docker compose exec odoo odoo shell -d wifimax_dev --stop-after-init

# Ver el estado de un módulo directamente en la base de datos
docker compose exec odoo psql -h db -U odoo -d wifimax_dev \
  -c "SELECT name, state FROM ir_module_module WHERE name = 'wifimax_valeria';"
```

---

## Problemas comunes y solución

### `permission denied while trying to connect to the docker API`

No cerraste sesión después de agregarte al grupo `docker`. Cierra sesión por completo y vuelve a entrar, o usa `newgrp docker` como solución temporal en la terminal actual.

### El contenedor de Odoo está en `Restarting` en bucle

Revisa los logs:
```bash
docker compose logs odoo
```
Si dice `grep: /etc/odoo/odoo.conf: No such file or directory`, falta el archivo `config/odoo.conf`. Créalo con el contenido de este README.

### Error al instalar el módulo: `No se encontraron registros que coincidan con id externo 'model_..._conversation'`

El módulo nunca se instaló correctamente antes. Instálalo desde terminal usando `-i`, no `-u`:
```bash
docker compose exec odoo odoo -d wifimax_dev -i wifimax_valeria --stop-after-init
```

### `ERR_CONNECTION_REFUSED` en el navegador al entrar a `localhost:8069`

El contenedor de Odoo no está corriendo o sigue iniciando. Verifica con `docker compose ps` y espera unos segundos, o revisa los logs si sigue sin levantar.

---

## Roles del equipo

| Rol | Encargado de |
|---|---|
| **Desarrollo de Software** | Módulo Odoo `wifimax_valeria` + microservicio Node.js, integración Claude API, Twilio, ElevenLabs, WhatsApp, OpenPay |
| **Redes #1** (MikroTik + Telefonía) | Conector MikroTik PPPoE, SIP Trunk, mapeo de números de Wifimax a Twilio |
| **Redes #2** (LibreNMS + Servicios) | Conector LibreNMS, mapeo de clientes a infraestructura, diagnóstico técnico |

---

## Roadmap

- [x] Entorno Docker + Odoo 18 Community
- [x] Scaffold del módulo `wifimax_valeria`
- [x] Modelo `wifimax.valeria.conversation`
- [ ] Modelo `wifimax.valeria.message`
- [ ] Scaffold del microservicio Node.js
- [ ] Primera llamada de prueba vía Twilio
- [ ] Integración Claude API (personalidad de Valeria)
- [ ] Integración ElevenLabs (voz)
- [ ] Identificación de cliente por número telefónico
- [ ] Consulta de saldo y estado de servicio
- [ ] Integración OpenPay (pagos SPEI/CoDi)
- [ ] WhatsApp Business API
- [ ] Agenda de visitas técnicas
- [ ] Escalación inteligente a humano
- [ ] Despliegue a producción

Cronograma completo de 16 semanas disponible en el documento de planeación del proyecto (no incluido en este repositorio por contener información interna de la empresa).

---

## Licencias y uso de software

Este proyecto usa **Odoo 18 Community**, la versión oficial y gratuita distribuida por Odoo S.A. a través de Docker Hub (`odoo:18`). No se utiliza ningún software modificado para evadir licencias de Odoo Enterprise. Si en el futuro se requiere una funcionalidad exclusiva de Enterprise, debe evaluarse la adquisición de una licencia oficial.
