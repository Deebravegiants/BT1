# [M] OpenClaw: Read-scoped identity-bearing HTTP clients could kill sessions via /sessions/:sessionKey/kill

## Summary
Severity: Medium
Advisory: GHSA-5hff-46vh-rxmw
CVE: CVE-2026-41298
CWE: CWE-269, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-5hff-46vh-rxmw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, `POST /sessions/:sessionKey/kill` did not enforce write scopes in identity-bearing HTTP modes. A caller limited to read-only operator scopes could still terminate a running subagent session.

## Impact

A read-scoped caller could perform a write-class control-plane mutation and interrupt delegated work. This was an authorization bug on the HTTP scope boundary, not a shared-secret compatibility exception.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `54a0878517167c6e49900498cf77420dadb74beb` — enforce session-kill HTTP scopes

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @EaEa0001 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5hff-46vh-rxmw
- https://nvd.nist.gov/vuln/detail/CVE-2026-41298
- https://github.com/openclaw/openclaw/commit/54a0878517167c6e49900498cf77420dadb74beb
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-session-termination-endpoint
