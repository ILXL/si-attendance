### SI Attendance App

A unified full-stack web application for students attending SI sessions (at CSUF) to log attendance.

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



