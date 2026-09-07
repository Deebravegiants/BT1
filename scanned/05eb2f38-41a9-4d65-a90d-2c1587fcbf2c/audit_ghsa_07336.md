# [M] New API is vulnerable to CSRF through user email binding

## Summary
Severity: Medium
Advisory: GHSA-26v7-h57m-gh9m
CVE: CVE-2026-44342
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-26v7-h57m-gh9m
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <0.12.0-alpha.1

## Details
## Summary

The email and WeChat account binding endpoints used GET requests for state-changing account operations. In deployments where session cookies could be sent on cross-site navigations, an attacker could trigger a logged-in user's browser to bind an attacker-controlled email address or OAuth identity.

Affected endpoints included:

- `GET /api/oauth/email/bind`
- `GET /api/oauth/wechat/bind`

## Impact

A successful attack could change account binding state. For email binding, the attacker could bind an email address they control and then attempt follow-on account recovery flows. The default session cookie configuration uses `SameSite=Strict`, which mitigates common cross-site navigation attacks in modern browsers, so the issue is rated Medium.

## Affected versions

Versions before `v0.12.0-alpha.1` are affected.

## Patches

This issue is fixed in `v0.12.0-alpha.1`. The fix changes email and WeChat binding routes from GET to POST and reads parameters from a JSON request body instead of query parameters. The same change set also normalizes password reset responses to avoid disclosing whether an email is registered.

## Workarounds

If upgrading immediately is not possible, ensure session cookies are configured with strict SameSite behavior and block GET requests to `/api/oauth/email/bind` and `/api/oauth/wechat/bind` at the reverse proxy.

## Resources

- Fixed by commit `e099117c61391abdf888fb75e382a582e550bd0e`.
- Relevant code paths: `router/api-router.go` and `controller/user.go`.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-26v7-h57m-gh9m
- https://github.com/QuantumNous/new-api/commit/e099117c61391abdf888fb75e382a582e550bd0e
- https://github.com/QuantumNous/new-api
