# 🔧 LIBRIS Deployment Troubleshooting Guide

## Common Deployment Errors & Solutions

### Error 1: ModuleNotFoundError - "from core.libris_agent import LIBRISAgent"

**Error Message:**
```
ModuleNotFoundError: This app has encountered an error.
File "/mount/src/libris/streamlit_app.py", line 20, in <module>
    from core.libris_agent import LIBRISAgent
```

**Cause:** Python can't find the LIBRIS modules because the import path isn't set correctly.

**Solution:** ✅ FIXED! The updated `streamlit_app.py` now includes:
```python
# Fix import path for Streamlit Cloud
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
```

**Action Required:**
1. Download the updated `streamlit_app.py` file
2. Commit and push to GitHub:
   ```bash
   git add streamlit_app.py
   git commit -m "Fix import path for Streamlit Cloud"
   git push
   ```
3. Streamlit Cloud will auto-redeploy in ~2 minutes

---

### Error 2: Missing __init__.py Files

**Error Message:**
```
ModuleNotFoundError: No module named 'core'
```

**Cause:** Python package directories are missing `__init__.py` files.

**Solution:** Ensure these files exist:
```
core/__init__.py
processors/__init__.py
extractors/__init__.py
search/__init__.py
exporters/__init__.py
knowledge_base/__init__.py
```

**Action Required:**
```bash
# Create all __init__.py files
touch core/__init__.py
touch processors/__init__.py
touch extractors/__init__.py
touch search/__init__.py
touch exporters/__init__.py
touch knowledge_base/__init__.py

git add */__init__.py
git commit -m "Add __init__.py files"
git push
```

---

### Error 3: Missing Dependencies

**Error Message:**
```
ModuleNotFoundError: No module named 'pdfplumber'
```

**Cause:** Required Python packages not listed in `requirements.txt`.

**Solution:** Verify `requirements.txt` contains:
```txt
streamlit>=1.28.0
pdfplumber>=0.9.0
pypdf>=3.0.0
python-docx>=0.8.11
pandas>=1.5.0
openpyxl>=3.0.0
```

**Action Required:**
```bash
# Verify requirements.txt
cat requirements.txt

# If missing packages, add them and push
git add requirements.txt
git commit -m "Update requirements.txt"
git push
```

---

### Error 4: File Not Found - knowledge_base/libris_catalog.json

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'knowledge_base/libris_catalog.json'
```

**Cause:** The knowledge base directory or file doesn't exist.

**Solution:** The app automatically creates the catalog on first run, but we need to ensure the directory structure exists.

**Action Required:**
Ensure `knowledge_base/` directory exists with `base_collection.py`:
```bash
ls -la knowledge_base/
# Should show: __init__.py, base_collection.py

git add knowledge_base/
git commit -m "Ensure knowledge base directory"
git push
```

**Note:** The `libris_catalog.json` file is auto-generated - don't commit it (it's in .gitignore).

---

### Error 5: Import Error - Circular Dependencies

**Error Message:**
```
ImportError: cannot import name 'X' from partially initialized module
```

**Cause:** Circular import dependencies between modules.

**Solution:** The LIBRIS code is designed to avoid this, but if it occurs:

1. Check that imports are at the module level, not function level
2. Verify no circular dependencies in code
3. Ensure all `__init__.py` files are empty or minimal

---

### Error 6: PDF Processing Fails

**Error Message:**
```
Error: PDF processing failed
```

**Cause:** Missing system-level PDF tools.

**Solution:** Add `packages.txt` file with:
```
poppler-utils
```

**Action Required:**
```bash
# Create packages.txt
echo "poppler-utils" > packages.txt

git add packages.txt
git commit -m "Add system dependencies"
git push
```

---

### Error 7: Slow or Timeout

**Error Message:**
```
TimeoutError: Request timed out
```

**Cause:** Heavy processing on large files or catalog.

**Solution:** Optimize with caching:

```python
@st.cache_resource
def load_agent():
    return LIBRISAgent()
```

This is already implemented in `streamlit_app.py`.

---

## Quick Diagnostic Checklist

Run through this checklist if your app won't deploy:

- [ ] `streamlit_app.py` exists in repository root
- [ ] `requirements.txt` exists with all dependencies
- [ ] `packages.txt` exists with system dependencies
- [ ] All directories have `__init__.py` files
- [ ] `.gitignore` exists
- [ ] Repository is PUBLIC on GitHub
- [ ] Main file path in Streamlit Cloud is `streamlit_app.py`
- [ ] Branch is `main` (not `master`)

---

## Testing Locally Before Deploy

Always test locally first:

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run streamlit_app.py

# Test all features:
# - Search works
# - Upload works (try small file first)
# - Export works
# - No errors in terminal
```

---

## Viewing Logs on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. Click "Manage app" (bottom right)
4. Click "Logs" tab
5. Look for error messages

Common log messages:
- `ModuleNotFoundError` → Check imports and __init__.py
- `FileNotFoundError` → Check file paths are relative
- `ImportError` → Check dependencies in requirements.txt

---

## Force Restart App

Sometimes you just need to restart:

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "⋮" (three dots)
4. Click "Reboot app"

---

## Nuclear Option: Fresh Deploy

If nothing works, start fresh:

```bash
# Delete Streamlit Cloud app
# (via dashboard)

# Re-deploy
# 1. Go to share.streamlit.io
# 2. New app
# 3. Select repository
# 4. Deploy
```

---

## Getting More Help

### Check These Resources First

1. **Streamlit Forum**: https://discuss.streamlit.io/
   - Search for your error message
   - Many common issues already solved

2. **Streamlit Docs**: https://docs.streamlit.io/
   - Deployment guide
   - Troubleshooting section

3. **GitHub Issues**: 
   - Check if others have same issue
   - Create new issue with error details

### Include These Details When Asking for Help

```
**Environment:**
- Repository: [your-repo-url]
- App URL: [your-app-url]
- Python version: 3.9 (Streamlit Cloud default)

**Error Message:**
[paste full error from logs]

**What I've Tried:**
- [list steps you've taken]

**Files Checklist:**
- streamlit_app.py: Yes/No
- requirements.txt: Yes/No
- packages.txt: Yes/No
- __init__.py files: Yes/No
```

---

## Prevention Tips

### Best Practices

1. **Test Locally First**: Always run `streamlit run streamlit_app.py` before deploying
2. **Small Commits**: Deploy incrementally, don't change everything at once
3. **Check Logs**: Monitor logs after each deploy
4. **Use .gitignore**: Don't commit generated files
5. **Pin Versions**: Use specific versions in requirements.txt (e.g., `streamlit==1.28.0`)

### File Structure Verification

Your repository should look like:

```
libris/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── core/
│   ├── __init__.py
│   └── libris_agent.py
├── processors/
│   ├── __init__.py
│   └── document_parser.py
├── extractors/
│   ├── __init__.py
│   └── bibliographic_extractor.py
├── search/
│   ├── __init__.py
│   └── intelligent_search.py
├── exporters/
│   ├── __init__.py
│   └── format_exporter.py
├── knowledge_base/
│   ├── __init__.py
│   └── base_collection.py
├── streamlit_app.py
├── requirements.txt
├── packages.txt
├── LICENSE
└── README.md
```

---

## Success Indicators

Your app is working when:

✅ App loads without errors  
✅ Search returns results  
✅ Upload processes files  
✅ Export downloads work  
✅ No errors in logs  
✅ App accessible at your URL

---

## Updated Files Available

All fixes have been applied to the deployment package. Download these updated files:

- ✅ `streamlit_app.py` - Fixed import paths
- ✅ `packages.txt` - Added system dependencies
- ✅ All `__init__.py` files verified
- ✅ `requirements.txt` - Optimized for Streamlit Cloud

**Push these files to GitHub and redeploy!**

---

*Last Updated: February 2026*  
*LIBRIS Deployment Troubleshooting Guide*
