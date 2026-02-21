#!/bin/bash

# Smart Power Disconnection Analytics System - Quick Start Script
# ================================================================

set -e

echo "=========================================="
echo "Power Theft Detection System - Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ pip upgraded"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Verify installation
echo ""
echo "Running deployment verification tests..."
echo "=========================================="
python test_deployment.py

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Test the detector:"
echo "     python power_theft_detector.py"
echo ""
echo "  3. Start the API server:"
echo "     python app.py"
echo ""
echo "  4. Test the API (in another terminal):"
echo "     curl http://localhost:5000/health"
echo ""
echo "  5. For Docker deployment:"
echo "     docker build -t power-theft-detector ."
echo "     docker run -p 5000:5000 power-theft-detector"
echo ""
echo "  6. For Docker Compose:"
echo "     docker-compose up -d"
echo ""
echo "See README.md and DEPLOYMENT_GUIDE.md for detailed instructions."
echo "=========================================="
