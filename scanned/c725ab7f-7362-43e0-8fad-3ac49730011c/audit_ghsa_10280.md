# [H] engram: HTTP server CORS wildcard + auth-off-by-default enables CSRF graph exfiltration and persistent indirect prompt injection

## Summary
Severity: High
Advisory: GHSA-2r2p-4cgf-hv7h
CWE: CWE-1188, CWE-306, CWE-352, CWE-942
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-2r2p-4cgf-hv7h
Type: github-advisory

## Affected
- npm: `engramx` — affected >=0 <2.0.2

## Details
### Summary

The local HTTP server started by `engram server` (binding `127.0.0.1:7337` by default) was exposed to any browser origin with no authentication unless `ENGRAM_API_TOKEN` was explicitly set. Combined with `Access-Control-Allow-Origin: *` on every response and a body parser that did not require `Content-Type: application/json`, this allowed a malicious web page the developer visited to:

1. **Exfiltrate** the local knowledge graph via `GET /query` and `GET /stats` (function names, file layout, recorded decisions/mistakes).
2. **Inject persistent prompt-injection payloads** via `POST /learn`, which wrote `mistake`/`decision` nodes that were later surfaced as system-reminders to the user's AI coding agent on every future session and file edit.

Severity: **High** — confidentiality + persistent indirect prompt injection against the user's coding agent.

### Affected versions

`engramx` >= 1.0.0, < 2.0.2 — any version that shipped the HTTP server.

### Patched in

`engramx@2.0.2`

### Workarounds (if you cannot upgrade)

- Do **not** run `engram server` or `engram ui`.
- If developers must, set `ENGRAM_API_TOKEN` to a long random value and terminate the server before browsing the web.

### Remediation (applied in 2.0.2)

1. Fail-closed auth on every non-public route — Bearer header or HttpOnly cookie, constant-time comparison, 256-bit auto-generated token at `~/.engram/http-server.token` (0600).
2. Wildcard CORS removed entirely; default is no CORS headers. Opt-in allowlist via `ENGRAM_ALLOWED_ORIGINS`.
3. Host + Origin validation — rejects DNS rebinding and Host spoofing.
4. `Content-Type: application/json` enforced on mutations — blocks the text/plain CSRF vector.
5. `/ui?token=` bootstrap with `Sec-Fetch-Site` gate — prevents cross-origin oracle probing.

### Credit

Discovered and responsibly disclosed by @gabiudrescu in engram issue #7.

## References
- https://github.com/NickCirv/engram/security/advisories/GHSA-2r2p-4cgf-hv7h
- https://github.com/NickCirv/engram/issues/7
- https://github.com/NickCirv/engram
