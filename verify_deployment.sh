#!/bin/bash
# LIBRIS Pre-Deployment Verification Script
# Run this before deploying to catch common issues

echo "🔍 LIBRIS Pre-Deployment Verification"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Verify we're in the right directory
echo "✓ Checking directory structure..."
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ ERROR: streamlit_app.py not found"
    echo "   Make sure you're in the libris directory"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ streamlit_app.py found"
fi

# Check 2: Verify core modules exist
echo ""
echo "✓ Checking core modules..."
MODULES=("core" "processors" "extractors" "search" "exporters" "knowledge_base")
for module in "${MODULES[@]}"; do
    if [ ! -d "$module" ]; then
        echo "  ❌ ERROR: $module/ directory missing"
        ERRORS=$((ERRORS + 1))
    elif [ ! -f "$module/__init__.py" ]; then
        echo "  ⚠️  WARNING: $module/__init__.py missing - creating it"
        touch "$module/__init__.py"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✓ $module/ OK"
    fi
done

# Check 3: Verify requirements.txt
echo ""
echo "✓ Checking requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    echo "  ❌ ERROR: requirements.txt not found"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ requirements.txt found"
    
    # Check for required packages
    REQUIRED_PACKAGES=("streamlit" "pdfplumber" "pypdf" "python-docx" "pandas" "openpyxl")
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! grep -q "$package" requirements.txt; then
            echo "  ⚠️  WARNING: $package not in requirements.txt"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
fi

# Check 4: Verify packages.txt
echo ""
echo "✓ Checking packages.txt..."
if [ ! -f "packages.txt" ]; then
    echo "  ⚠️  WARNING: packages.txt not found - creating it"
    echo "poppler-utils" > packages.txt
    WARNINGS=$((WARNINGS + 1))
else
    echo "  ✓ packages.txt found"
fi

# Check 5: Verify .gitignore
echo ""
echo "✓ Checking .gitignore..."
if [ ! -f ".gitignore" ]; then
    echo "  ⚠️  WARNING: .gitignore not found"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  ✓ .gitignore found"
fi

# Check 6: Verify knowledge base
echo ""
echo "✓ Checking knowledge base..."
if [ ! -d "knowledge_base" ]; then
    echo "  ❌ ERROR: knowledge_base/ directory missing"
    ERRORS=$((ERRORS + 1))
elif [ ! -f "knowledge_base/base_collection.py" ]; then
    echo "  ❌ ERROR: knowledge_base/base_collection.py missing"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ knowledge_base/ OK"
fi

# Check 7: Verify .streamlit config
echo ""
echo "✓ Checking Streamlit configuration..."
if [ ! -d ".streamlit" ]; then
    echo "  ⚠️  WARNING: .streamlit/ directory missing"
    WARNINGS=$((WARNINGS + 1))
elif [ ! -f ".streamlit/config.toml" ]; then
    echo "  ⚠️  WARNING: .streamlit/config.toml missing"
    WARNINGS=$((WARNINGS + 1))
else
    echo "  ✓ .streamlit/config.toml found"
fi

# Check 8: Test imports (if Python available)
echo ""
echo "✓ Testing Python imports..."
if command -v python3 &> /dev/null; then
    if python3 -c "import sys; sys.path.insert(0, '.'); from core.libris_agent import LIBRISAgent" 2>/dev/null; then
        echo "  ✓ Python imports working"
    else
        echo "  ❌ ERROR: Python import test failed"
        echo "     Try running: pip install -r requirements.txt"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ⚠️  Python not found - skipping import test"
fi

# Summary
echo ""
echo "======================================"
echo "📊 Verification Summary"
echo "======================================"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ All critical checks passed!"
    echo ""
    echo "🚀 Ready to deploy to Streamlit Cloud!"
    echo ""
    echo "Next steps:"
    echo "1. Commit any changes: git add . && git commit -m 'Pre-deployment fixes'"
    echo "2. Push to GitHub: git push"
    echo "3. Deploy on share.streamlit.io"
    echo ""
    exit 0
else
    echo "❌ Found $ERRORS critical error(s)"
    echo ""
    echo "Please fix the errors above before deploying."
    echo "See TROUBLESHOOTING.md for help."
    echo ""
    exit 1
fi
