# [M] Ech0  authenticated user-list exposed data via public `/api/allusers` endpoint  

## Summary
Severity: Medium
Advisory: GHSA-m983-7426-5hrj
CVE: CVE-2026-33638
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-m983-7426-5hrj
Type: github-advisory

## Affected
- Go: `github.com/lin-snow/ech0` — affected >=0 <1.4.8-0.20260322121226-acbf1fd71011

## Details
### Summary
A public access-control flaw allows unauthenticated users to retrieve the full user list from `GET /api/allusers`. This exposes user profile metadata to anyone who can reach the application and enables remote user enumeration.

### Details
The vulnerable route is registered as a public endpoint:

- `internal/router/user.go:17`
  - `appRouterGroup.PublicRouterGroup.GET("/allusers", h.UserHandler.GetAllUsers())`

However, the handler appears to have been intended as an authenticated endpoint:

- `internal/handler/user/user.go:177-185`
  - API annotations indicate an authentication requirement via `@Security ApiKeyAuth`

This creates a mismatch between the documented security model and the actual routing configuration. As a result, requests to `GET /api/allusers` succeed without authentication and return user records, including profile metadata such as usernames, email addresses, role-related flags, avatar values, and locale information.

A negative control against another endpoint that correctly requires authentication further supports that this exposure is unintended: `GET /api/user` returns `401 Unauthorized` when no token is supplied, while `GET /api/allusers` remains publicly accessible.

### Impact
- **Type:** Access control bypass / unauthenticated data exposure
- **Who is impacted:** Any deployment exposing the API to untrusted networks, and all users whose profile metadata is returned by the endpoint
- **Security impact:** Enables remote user enumeration and disclosure of user profile metadata, which may facilitate account reconnaissance, phishing, and targeted credential attacks
- **Attack preconditions:** None beyond network access to the affected API endpoint

## References
- https://github.com/lin-snow/Ech0/security/advisories/GHSA-m983-7426-5hrj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33638
- https://github.com/lin-snow/Ech0/commit/acbf1fd71011e6b9e1e6a911128056a19862f681
- https://github.com/lin-snow/Ech0
- https://github.com/lin-snow/Ech0/releases/tag/v4.2.0
