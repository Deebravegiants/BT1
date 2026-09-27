# [H] Sim Studio AI - Unauthenticated OAuth Token Theft

## Summary
Severity: High
Advisory: CVE-2026-3432
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2026-3432
Type: osv

## Details
On SimStudio version below to 0.5.74, the `/api/auth/oauth/token` endpoint contains a code path that bypasses all authorization checks when provided with `credentialAccountUserId` and `providerId` parameters. An unauthenticated attacker can retrieve OAuth access tokens for any user by supplying their user ID and a provider name, effectively stealing credentials to third-party services.

## References
- https://www.tenable.com/security/research/tra-2026-13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3432
- https://github.com/simstudioai/sim
