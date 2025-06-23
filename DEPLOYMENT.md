# Deployment Guide for DWG Analyzer

## Render Deployment Fix

The deployment issue was caused by Python 3.13.4 incompatibility with the reportlab package. Here's how to fix it:

### 1. Python Version Constraint
- Updated `pyproject.toml` to require Python `>=3.11,<3.13`
- Added `runtime.txt` specifying Python 3.12.0
- Created `pyproject_render.toml` with proper Poetry configuration

### 2. Deployment Configuration
- `render.yaml`: Configured for Render deployment with proper build commands
- `Procfile`: Set up for web service startup
- Environment variables configured for PostgreSQL database

### 3. Build Process
The deployment will:
1. Use Python 3.12.0 (compatible with reportlab)
2. Copy `pyproject_render.toml` to `pyproject.toml`
3. Install dependencies via Poetry
4. Start Streamlit server on the assigned port

### 4. Database Connection
PostgreSQL database is pre-configured with credentials from your Render setup.

### Next Steps
1. Push these changes to your GitHub repository
2. Deploy on Render using the updated configuration
3. The app will be available at your Render URL

The Python version constraint fix ensures reportlab and all other dependencies install correctly on Render's infrastructure.