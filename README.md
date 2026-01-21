### SI Attendance App

A unified full-stack web application for students attending SI sessions (at CSUF) to log attendance.

## Quick Start

- Clone repo and open in VS Code dev container.
- Set env vars in `src/.env` (see Environment Setup).
- Build frontend and auto-copy to `src/static/`:
  ```bash
  cd src/frontend
  npm install
  npm run build
  ```
- Run locally (serves frontend + API):
  ```bash
  cd ../src
  export FLASK_APP=index.py
  python -m flask run
  ```
- Deploy to production (run from `src/`):
  ```bash
  cd /workspaces/si-attendance/src
  vercel --prod
  ```

**Monorepo structure:**
- `/src`: Flask backend API
- `/frontend`: Svelte frontend

##### Simplified Workflow Diagram

![](./media/si_attendance_workflow.png)

##### Massive thanks to Aaron Lieberman (HTTP/REST guru)

## Environment Setup

The backend requires three environment variables. Create a `.env` file in `/src`:

```env
CREDS_JSON="<entire Google Service Account key as a JSON string>"
secretKioskUsername="<kiosk login username>"
secretKioskPassword="<kiosk login password>"
```

**CREDS_JSON format:** Download a Service Account key from Google Cloud Console (JSON format), then paste its full contents as a single-line string:
```json
{"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}
```

## Development

### Backend only:
```sh
cd src
export FLASK_APP=index.py
python -m flask run
```

### Frontend only:
```sh
cd frontend
npm install
npm run dev
```

### Full stack (from root):
```sh
cd frontend && npm run build  # Build frontend static files
cd ../src
export FLASK_APP=index.py
python -m flask run           # Serves frontend at / and API at /signin, /getcourses, etc.
```

## Deployment

### With Vercel:

1. Set environment variables in Vercel Project Settings:
   - `CREDS_JSON`
   - `secretKioskUsername`
   - `secretKioskPassword`

2. Deploy:
```sh
vercel deploy   # Preview
vercel --prod   # Production
```

The monorepo `vercel.json` automatically:
- Builds the Svelte frontend (`npm run build`)
- Deploys the Flask backend
- Routes `/signin`, `/getcourses`, `/noncwidsignin` to the backend
- Serves the frontend for all other paths

## Build and Update (Production)

### One-time setup
- Frontend lives in `src/frontend/` (Svelte + Rollup)
- Deployed static assets live in `src/static/` alongside the backend
- Vercel deploys from `src/` using `vercel.json` and includes files listed under `includeFiles`

### Update frontend after making changes
1. Build the Svelte app and auto-copy build output to `src/static/`:
  ```sh
  cd src/frontend
  npm install             # first time only
  npm run build           # builds and copies files to ../static/
  ```
  The build step copies:
  - `public/index.html`, `public/global.css`, `public/favicon.png` → `src/static/`
  - `public/build/*` → `src/static/build/`

2. Commit updated static files:
  ```sh
  cd ../../src
  git add static/
  git commit -m "Update frontend build"
  ```

3. Deploy from local (recommended in this repo):
  ```sh
  cd /workspaces/si-attendance/src
  vercel --prod
  ```

### Update backend
1. Edit Python files under `src/`
2. Commit changes
3. Deploy (same command):
  ```sh
  cd /workspaces/si-attendance/src
  vercel --prod
  ```

### Local testing (full stack)
```sh
cd src/frontend && npm run build   # produce static assets
cd ../src
export FLASK_APP=index.py
python -m flask run                # serves static files from src/static and APIs
```

### Troubleshooting
- If the frontend doesn't load on Vercel:
  - Ensure `src/static/` contains `index.html` and `build/bundle.js`
  - Verify `src/vercel.json` has `includeFiles` entries for `static/**`
  - Deploy from `src/` (not repo root): `cd src && vercel --prod`
- If you change Svelte code, always run `npm run build` before deploying.

## API Endpoints

- **GET `/signin`**: Sign in a student
  - Query params: `cwid`, `course`
- **GET `/getcourses`**: Get available courses for a CWID
  - Query params: `cwid`
- **GET `/noncwidsignin`**: Log a non-CWID student
  - Query params: `course`, `nonCWIDStatus`, `name`

## Contributing

1. Make changes to `/frontend` (Svelte) or `/src` (Flask)
2. Test locally
3. `vercel deploy` # Preview
4. `vercel --prod` # Production



