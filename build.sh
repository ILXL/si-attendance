#!/bin/bash
# Vercel build script - runs before Python functions are deployed
echo "Installing dependencies..."
cd src && pip install -r requirements.txt

echo "Copying frontend files for deployment..."
# Copy the entire src/frontend directory to be accessible at runtime
if [ -d "frontend" ]; then
    echo "Frontend directory found: $(ls -la frontend/public/build/ 2>/dev/null || echo 'build not found')"
fi
