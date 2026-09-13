# [C] Network-AI: CVE-2026-46701 fix incomplete — empty default secret still authorizes all requests

## Summary
Severity: Critical
Advisory: GHSA-r78r-rwrf-rjwp
CVE: CVE-2026-48814
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-r78r-rwrf-rjwp
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=0 <5.7.2

## Details
## Advisory / Disclosure

# Network-AI — CVE-2026-46701 fix is incomplete: the "Empty Default Secret" unauth path survives

**Target:** Jovancoding/Network-AI (npm `network-ai`), **latest v5.7.1**
**Status:** the advisory ("Unauthenticated Cross-Origin MCP Tool Invocation via Empty
Default Secret") named three flaws. The fix (5.4.5) closed the **CORS** flaw
(`Access-Control-Allow-Origin` is now set only for localhost origins), but left the
**empty-default-secret** flaw the title is about: the SSE MCP server still defaults to an
empty secret, `_isAuthorized()` still returns `true` when the secret is empty, and a
non-loopback bind only **warns**. So the server still runs **fully unauthenticated by
default** — any non-browser caller (curl, SSRF, or a `0.0.0.0` bind) can invoke all 22 MCP
tools (`config_set`, `agent_spawn`, `blackboard_write`, `token_*`) with no credentials.
**Class:** CWE-306/CWE-862 Missing Authentication — incomplete fix.
**Methodology:** M1 incomplete-fix audit (anchor = the 5.4.5 fix; sibling-walk on latest v5.7.1, executed).
**Severity:** High (matches parent; the browser amplifier is removed, so exploitation now
needs non-browser reach — SSRF or a non-loopback bind, which the fix only warns about).

## What the fix did and didn't do (verified on latest v5.7.1)
| advisory flaw | latest v5.7.1 |
|---|---|
| wildcard CORS (`ACAO: *`) | **FIXED** — `lib/mcp-transport-sse.ts` sets `ACAO` only when `origin` matches `^https?://(localhost\|127\.0\.0\.1)(:\d+)?$` |
| empty default secret | **NOT FIXED** — `bin/mcp-server.ts`: `secret: process.env['NETWORK_AI_MCP_SECRET'] ?? ''` |
| `_isAuthorized` open on empty secret | **NOT FIXED** — `if (!this._opts.secret) return true;` |
| require secret / refuse unauth bind | **NOT DONE** — `listen()` only `process.stderr.write('… WARNING …')` on non-loopback bind, then listens anyway |

The advisory's remediation #1 ("Require a non-empty secret at startup … `process.exit(1)`")
was not implemented.

## PoC (executed against the latest source, v5.7.1) — `poc/legend-networkai-empty-secret.ts`
Instantiates the real `McpSseServer` from the latest `lib/` with a mock bridge and the
**default (empty) secret**, then issues requests (run-log `poc/run-log.txt`):

```
POST /mcp  no-auth, no-origin (curl/SSRF) -> HTTP 200, dispatched=true
   body: {"jsonrpc":"2.0","id":1,"result":{"executed":true,"tool":"config_set"}}
POST /mcp  Origin: evil.example.com        -> ACAO=undefined   (CORS half fixed)
```
The no-auth request passes `_isAuthorized` and reaches `handleRPC` (tool dispatched) — i.e.
unauthenticated tool invocation persists on the latest release; only the browser-CORS read
amplifier was removed.

Run: from a v5.7.1 checkout, `npm i` then
`npx ts-node --transpile-only poc/legend-networkai-empty-secret.ts`.

## Recommended fix
Implement the advisory's remediation #1: refuse to start SSE mode with an empty secret
(unless `--stdio`), and/or change `_isAuthorized` to fail closed (an empty configured
secret should mean "deny", not "allow"). The CORS allowlist alone does not authenticate
non-browser callers.

## Precondition / honesty
With CORS now localhost-only, the drive-by *browser* attack is mitigated. The residual
requires a non-browser path to the port: an SSRF on the host, or the operator binding to a
non-loopback address (Docker/remote), which the fix only warns about. The empty secret
remains the shipped default and `_isAuthorized` still authorizes it.

## Credits

@Kai Aizen / @SnailSploit — https://snailsploit.com

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-r78r-rwrf-rjwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-48814
- https://github.com/Jovancoding/Network-AI
- https://github.com/Jovancoding/Network-AI/releases/tag/v5.7.2
- https://github.com/advisories/GHSA-j3vx-cx2r-pvg8
