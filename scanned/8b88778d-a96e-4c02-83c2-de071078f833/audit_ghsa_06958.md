# [M] Coder's subdomain workspace app routing trusts unauthenticated X-Forwarded-Host header, enabling cross-app data access

## Summary
Severity: Medium
Advisory: GHSA-5g4w-3vw9-478w
CVE: CVE-2026-55430
CWE: CWE-345, CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-5g4w-3vw9-478w
Type: github-advisory

## Affected
- Go: `github.com/coder/coder/v2` — affected >=2.34.0 <2.34.2
- Go: `github.com/coder/coder/v2` — affected >=2.33.0 <2.33.8
- Go: `github.com/coder/coder/v2` — affected >=2.30.0 <2.32.7
- Go: `github.com/coder/coder/v2` — affected >=0 <2.29.17

## Details
### Summary

The workspace app proxy resolves the target app from `httpapi.RequestHost()` which prefers the `X-Forwarded-Host` header over the real `Host` header. No middleware strips `X-Forwarded-Host` before routing and the header is not browser-forbidden so client-side JavaScript can set it on `fetch()` calls.

> **Note:** Practical exploitation requires subdomain app routing (wildcard hostname) enabled, a victim who visits the attacker's shared app and a deployment whose upstream proxy does not strip `X-Forwarded-Host`.

### Impact

App session cookies are scoped to the wildcard parent domain so the browser attaches them to any app subdomain. An attacker who controls a shared workspace app can serve JavaScript that sends same-site requests with a forged `X-Forwarded-Host` pointing at a victim's private app. The server routes by the attacker-controlled header but authorizes with the victim's cookie which lets the attacker read the victim's private app responses. Subdomain app routing must be enabled and no upstream proxy may strip `X-Forwarded-Host`.

### Patches

The fix trusts `X-Forwarded-Host` only from configured trusted proxies and otherwise resolves the routing host from the verified request host.

The fix was backported to all supported release lines:

| Release line | Patched version |
|---|---|
| 2.34 | [v2.34.2](https://github.com/coder/coder/releases/tag/v2.34.2) |
| 2.33 | [v2.33.8](https://github.com/coder/coder/releases/tag/v2.33.8) |
| 2.32 | [v2.32.7](https://github.com/coder/coder/releases/tag/v2.32.7) |
| 2.29 (ESR) | [v2.29.17](https://github.com/coder/coder/releases/tag/v2.29.17) |

### Workarounds

Place an upstream reverse proxy that strips or overwrites `X-Forwarded-Host` on untrusted requests.

### Resources

- Fix: #26204

### Credits

Coder would like to thank Anthropic's Security Team (ANT-2026-22435) for independently disclosing this issue!

## References
- https://github.com/coder/coder/security/advisories/GHSA-5g4w-3vw9-478w
- https://github.com/coder/coder/pull/26204
- https://github.com/coder/coder
