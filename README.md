# YERUZZA STUDIO - Documentación del Proyecto

---

## Descripción General

Este proyecto es una aplicación web full-stack que consta de:

- **Frontend:** SPA React 18 con Vite, JavaScript y CSS propio.
- **Backend:** API REST con FastAPI, autenticación JWT, y persistencia en PostgreSQL con fallback a SQLite.
- **Servidor Web:** Nginx que sirve la SPA y hace proxy inverso a la API.
- **Orquestación:** Docker Compose con tres servicios: `db` (PostgreSQL), `api` (FastAPI) y `web` (Nginx + React).

La aplicación está preparada para desplegarse en Dokploy, con configuración para exponer el frontend en el puerto 8080.

---

## Contenido del Proyecto

- `README.md` — Esta documentación.
- `api/` — Código backend FastAPI y Dockerfile.
- `src/` — Código frontend React.
- `web.Dockerfile` — Dockerfile multi-stage para construir y servir la SPA.
- `docker-compose.yml` — Orquestación de servicios.
- `nginx.conf` — Configuración Nginx para SPA y proxy API.
- `package.json` y `vite.config.js` — Configuración frontend.
- `index.html` — Archivo HTML principal.
- `src/style.css` — Estilos CSS propios.

---

## Requisitos Previos

- Docker y Docker Compose instalados.
- Node.js y npm (para desarrollo local frontend).
- Python 3.12+ (para desarrollo local backend).
- Acceso a Dokploy para despliegue.

---

## Uso Local

### 1. Levantar la base de datos PostgreSQL

El servicio `db` se levanta automáticamente con Docker Compose y crea la base de datos `producto` con usuario y contraseña `studio`.

### 2. Backend FastAPI

Desde la carpeta `api/`:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- La API estará disponible en `http://localhost:8000/api`.
- Endpoints importantes:
  - `POST /api/auth/register` — Registro de usuario.
  - `POST /api/auth/login` — Login y obtención de token JWT.
  - `GET /api/auth/me` — Información del usuario autenticado.
  - Rutas CRUD protegidas bajo `/api` requieren token JWT en header `Authorization: Bearer <token>`.
  - `GET /api/health` — Estado del servicio.

### 3. Frontend React

Desde la raíz del proyecto:

```bash
npm install
npm run dev
```

- La SPA estará disponible en `http://localhost:5173` (puerto por defecto de Vite).
- El frontend consume la API en `/api`.
- El token JWT se guarda en `localStorage` y se envía en cada petición protegida.
- Pantalla de login y registro con guardia de rutas para proteger contenido.

### 4. Levantar todo con Docker Compose

En la raíz del proyecto:

```bash
docker-compose up --build
```

- Servicios:
  - `db` en PostgreSQL 16-alpine.
  - `api` en FastAPI puerto 8000.
  - `web` en Nginx puerto 8080 (expuesto localmente).
- Acceder a la SPA en `http://localhost:8080`.

---

## Usuarios de Prueba

Para facilitar pruebas, puede usar estos usuarios de ejemplo (registrar vía `/auth/register` o insertar en base de datos):

| Usuario  | Contraseña |
| -------- | ---------- |
| testuser | testpass   |
| admin    | adminpass  |

---

## Despliegue en Dokploy

### 1. Configurar variables de entorno

- `AUTH_SECRET`: Clave secreta para JWT.
- `DATABASE_URL`: Cadena de conexión PostgreSQL, por ejemplo:

```
postgresql+psycopg://studio:studio@db:5432/producto
```

### 2. Levantar servicios

Dokploy usará el `docker-compose.yml` para levantar los tres servicios:

- `db` (PostgreSQL)
- `api` (FastAPI)
- `web` (Nginx + React)

### 3. Configurar dominio

Asignar el dominio deseado al puerto **8080** del servicio `web` para que la SPA sea accesible públicamente.

### 4. Notas

- El backend está disponible en `/api` vía proxy inverso.
- La SPA maneja rutas internas con React Router.
- El token JWT se gestiona en frontend y se envía en headers para rutas protegidas.

---

## Recomendaciones para Integraciones Futuras

- **Módulos de pasarelas de pago:** Diseñar un módulo desacoplado para integrar pasarelas según cliente.
- **Chat y bots:** Implementar bots web integrados para soporte, evitando dependencia exclusiva de WhatsApp.
- **Extensibilidad:** Mantener backend modular con routers y frontend con componentes reutilizables.
- **Seguridad:** Rotar `AUTH_SECRET` periódicamente y usar HTTPS en producción.
- **Monitorización:** Añadir endpoints y logs para monitoreo y alertas.

---

## Contacto

Para dudas o soporte, contactar con el equipo de desarrollo de YERUZZA STUDIO.

---

**¡Gracias por usar YERUZZA STUDIO!**