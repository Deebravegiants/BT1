# [C] WolfStack < 25.9.2 Hard-coded Secret Authentication Bypass via X-WolfStack-Secret

## Summary
Severity: Critical
Advisory: CVE-2026-73519
Aliases: GHSA-r3mw-2wmq-j6jg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73519
Type: osv

## Details
WolfStack before 25.9.2 contains a hard-coded cluster-authentication secret compiled into every build and published as a constant in src/auth/mod.rs, allowing remote unauthenticated attackers to bypass authentication by supplying this value in the X-WolfStack-Secret header to the require_auth() gate without any session, API key, or user account. Attackers can reach an affected node's management port to enumerate all Docker and LXC containers on the host and execute arbitrary commands as root inside any container via the POST /api/containers/{runtime}/{id}/exec endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73519.json
- https://github.com/wolfsoftwaresystemsltd/WolfStack/releases?page=7#release-v25.9.2
- https://github.com/wolfsoftwaresystemsltd/WolfStack/security/advisories/GHSA-r3mw-2wmq-j6jg
- https://nvd.nist.gov/vuln/detail/CVE-2026-73519
- https://www.vulncheck.com/advisories/wolfstack-hard-coded-secret-authentication-bypass-via-x-wolfstack-secret
- https://github.com/wolfsoftwaresystemsltd/WolfStack
