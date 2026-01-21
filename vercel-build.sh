#!/bin/bash
# This script runs as part of Vercel's Python build process
# It copies the frontend files to where Flask can find them at runtime

# The current directory during build is /var/task
# We need to copy src/frontend to a location where index.py can access it

if [ -d "src/frontend" ]; then
    echo "Copying frontend files to runtime directory..."
    cp -r src/frontend /var/task/frontend
    ls -la /var/task/frontend/public/build/ || echo "Frontend build directory not found"
else
    echo "WARNING: src/frontend directory not found"
fi

echo "Build script complete"
