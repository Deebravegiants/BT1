# [M] Payload does not invalidate JWTs after log out

## Summary
Severity: Medium
Advisory: GHSA-5v66-m237-hwf7
CVE: CVE-2025-4643
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-5v66-m237-hwf7
Type: github-advisory

## Affected
- npm: `payload` — affected >=0 <3.44.0
- npm: `@payloadcms/next` — affected >=0 <3.44.0
- npm: `@payloadcms/graphql` — affected >=0 <3.44.0

## Details
Payload uses JSON Web Tokens (JWT) for authentication. After log out JWT is not invalidated, which allows an attacker who has stolen or intercepted token to freely reuse it until expiration date (which is by default set to 2 hours, but can be changed). 

This issue has been fixed in version 3.44.0 of Payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4643
- https://github.com/payloadcms/payload/commit/26d709dda6e512ce347557eaa2057db6e0cbf809
- https://cert.pl/en/posts/2025/08/CVE-2025-4643
- https://github.com/payloadcms/payload
