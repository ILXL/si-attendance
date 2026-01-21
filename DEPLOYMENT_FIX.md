# Deployment Fix: Frontend Build Files Now Included

## Problem
The Svelte frontend build files were being ignored by git, preventing them from being deployed to Vercel. This caused the error "Frontend not available" on the deployed application.

## Root Cause Analysis
1. **src/frontend/.gitignore** contained `/public/build/` - excluding the compiled Svelte output
2. This is standard practice for development (build files are generated, not committed)
3. However, for Vercel deployment, the files need to be either:
   - Committed to git, OR
   - Generated as part of the Vercel build process

## Solution Implemented

### 1. Fixed src/frontend/.gitignore
**Removed:** `/public/build/` line
```diff
/node_modules/
-/public/build/

.DS_Store
.vercel
*.*.un~
.vscode
```

### 2. Removed Embedded Git Repository
- `src/frontend/` was imported with its own `.git` directory
- Removed `src/frontend/.git` to integrate it into the main repository
- This allowed the entire frontend to be tracked in the main git repo

### 3. Updated Deployment Configuration
**Files created/modified:**
- `.vercelignore` - Explicitly allows frontend files: `!src/frontend/public/**`
- `vercel.json` - Simplified to single Python build (Flask serves the frontend)
- `src/index.py` - Configured Flask to serve static files from `frontend/public/`

## What's Now Deployed
Frontend build artifacts committed to git:
- `src/frontend/public/build/bundle.js` (22.6KB) - Compiled Svelte app
- `src/frontend/public/build/bundle.css` (22.4KB) - Bundled styles
- `src/frontend/public/build/bundle.js.map` (108.9KB) - Source map
- `src/frontend/public/index.html` (393B) - Entry point
- `src/frontend/public/global.css` (1.7KB) - Global styles
- `src/frontend/public/favicon.png` - Icon

## Flask Static File Serving
In `src/index.py`:
```python
frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'public')
app = Flask(__name__, static_folder=frontend_path, static_url_path='')

@app.route('/')
@app.route('/<path:path>')
def serve_spa(path):
    # Serve static files (CSS, JS, etc.)
    if '.' in path:
        try:
            return send_from_directory(app.static_folder, path)
        except:
            pass
    # Fallback to index.html for SPA routing
    return send_from_directory(app.static_folder, 'index.html')
```

## Verification Steps

1. **Check git tracking:**
   ```bash
   git ls-files src/frontend/public/build/bundle.js
   ```
   Should show the file is tracked.

2. **Verify Flask serves frontend:**
   - Local: `python src/index.py` then visit http://localhost:5000
   - Should see the Svelte attendance app

3. **Verify Vercel deployment:**
   - Visit your Vercel app URL (e.g., si-attendance.vercel.app)
   - Should see the Svelte UI load
   - Click the `/debug` endpoint to verify:
     - `index_html_loaded: true`
     - `public_dir_exists: true`

4. **Test API endpoints:**
   - Sign in form should call `/signin?cwid=X&course=Y`
   - Verify it connects to the backend correctly

## Git Commits
- `2387af4` - feat: Include frontend build files and fix git structure for Vercel deployment
- `706c705` - chore: Update Python version file

## Next Steps
1. Verify Vercel has triggered a new deployment (check Vercel dashboard)
2. Test the deployed app at your Vercel URL
3. If issues persist, check Vercel build logs for any errors

## Technical Details
- **Python Runtime:** 3.12 (via `runtime.txt`)
- **Frontend Framework:** Svelte with Rollup bundler
- **Backend Framework:** Flask with Flask-RESTFUL
- **Static Files:** Served by Flask at runtime (not as separate Vercel static deployment)
- **CORS:** Enabled for all origins in Flask

## Why This Approach?
Rather than configuring Vercel to rebuild the frontend on every deployment, we commit the pre-built files. This is practical because:
1. Reduces build time on Vercel
2. Avoids Node.js dependency on Vercel (Svelte build is local)
3. Files are relatively small (~150KB total)
4. Ensures deterministic deployments (same build every time)
5. Flask serves them as static files efficiently
