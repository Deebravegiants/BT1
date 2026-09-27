# [C] OpenClaw: WebSocket shared-auth connections could self-declare elevated scopes

## Summary
Severity: Critical
Advisory: GHSA-rqpp-rjj8-7wv8
CVE: CVE-2026-22172
CWE: CWE-269, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-rqpp-rjj8-7wv8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

A logic flaw in the OpenClaw gateway WebSocket connect path allowed certain device-less shared-token or password-authenticated backend connections to keep client-declared scopes without server-side binding. A shared-authenticated client could present elevated scopes such as `operator.admin` even though those scopes were not tied to a device identity or an explicitly trusted Control UI path.

### Impact

This crossed the intended authorization boundary and could let a shared-secret-authenticated backend client perform admin-only gateway operations.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. The gateway now clears unbound scopes for non-Control-UI shared-auth connections, and regression tests cover the device-less shared-auth path.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rqpp-rjj8-7wv8
- https://github.com/openclaw/openclaw/pull/44306
- https://github.com/openclaw/openclaw/commit/5e389d5e7c9233ec91026ab2fea299ebaf3249f6
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
