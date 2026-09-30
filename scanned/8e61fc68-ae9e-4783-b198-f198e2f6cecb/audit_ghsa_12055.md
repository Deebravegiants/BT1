# [M] Gogs: Access tokens get exposed through URL params in API requests

## Summary
Severity: Medium
Advisory: GHSA-x9p5-w45c-7ffc
CVE: CVE-2026-26196
CWE: CWE-598
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-x9p5-w45c-7ffc
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0

## Details
### Summary

The Gogs API still accepts tokens in URL parameters such as `token` and `access_token`, which can leak through logs, browser history, and referrers.

### Details

A static review shows that the API still checks tokens in the URL query before looking at headers:

  - internal/context/auth.go reads `c.Query("token")`
  - internal/context/auth.go falls back to `c.Query("access_token")`
  - internal/context/auth.go only checks the `Authorization` header when the query token is empty
  - internal/context/auth.go authenticates using that token and marks the request as token-authenticated

Token-authenticated requests are accepted by API routes through `c.IsTokenAuth` checks:
  - internal/route/api/v1/api.go

### Impact

If tokens are sent in URLs such as `/api/v1/user?token=...`, they can leak in logs, browser or shell history, and referrer headers, and can be reused until revoked.

### Recommended Fix

- Authentication headers should be used exclusively for token transmission.
- Token parameters should be blocked at the proxy or WAF level.
- Query strings should be scrubbed from logs.
- A strict referrer policy should be set.

### Remediation

A fix is available at https://github.com/gogs/gogs/releases/tag/v0.14.2.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-x9p5-w45c-7ffc
- https://nvd.nist.gov/vuln/detail/CVE-2026-26196
- https://github.com/gogs/gogs/pull/8177
- https://github.com/gogs/gogs/commit/295bfba72993c372e7b338438947d8e1a6bed8fd
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.2
