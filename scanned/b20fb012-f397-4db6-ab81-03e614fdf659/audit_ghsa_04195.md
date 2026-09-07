# [C] @acastellon/auth: Authentication bypass via spoofable headers in validateToken()

## Summary
Severity: Critical
Advisory: GHSA-gfj5-979r-92pw
CVE: CVE-2026-58399
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-gfj5-979r-92pw
Type: github-advisory

## Affected
- npm: `@acastellon/auth` — affected >=0 <2.3.0

## Details
@acastellon/auth v2.2.0 appears to allow an unauthenticated authentication bypass in validateToken() through spoofable auth-user and Host request headers.

The validateToken middleware contains a service-to-service bypass for auth-user: service-brother when req.get('host').startsWith(getHostName()). Both values involved in the check can be influenced by an unauthenticated HTTP client: auth-user is a request header, and Host is also client-controlled. As a result, a remote unauthenticated attacker can send a request with crafted headers and bypass token validation before the normal legacy/JWT/OIDC validation logic runs.

Impact:
An attacker may be able to access routes protected by validateToken() without a valid token. In deployments where downstream services trust auth-user or is-* headers, this may also lead to privilege escalation.

Affected package:
@acastellon/auth v2.2.0

Affected code:
auth.js, validateToken()
The issue is related to the service-brother bypass and getHostName() check.

Example request:
```
GET /protected HTTP/1.1
Host: <configured CNAME or hostname>
auth-user: service-brother
is-admin: true
```

Expected behavior:
The request should require a valid authentication token.

Actual behavior:
The middleware calls next() before token validation.

Fix implemented in v2.3.0+:

Removed the spoofable bypass.
Always sanitize incoming auth-user and is-* headers.
Added mTLS client certificate based service auth (with optional TRUSTED_MTLS_SERVICES allowlist).
Updated consumers (rest, graphql, dns-client) for mTLS support.
Unit tests added for sanitization + mTLS path.

## References
- https://github.com/antonio-castellon/module-auth/security/advisories/GHSA-gfj5-979r-92pw
- https://github.com/antonio-castellon/module-auth/issues/6
- https://github.com/antonio-castellon/module-auth
- https://www.npmjs.com/package/@acastellon/auth/v/2.3.0
