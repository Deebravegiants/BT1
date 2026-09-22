# [C] Dokploy: Pre-Auth Admin Takeover via Hardcoded Authentication Secret

## Summary
Severity: Critical
Advisory: CVE-2026-45631
Aliases: GHSA-w3gm-rc4p-9rhj
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45631
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). From 0.27.0 to before 0.29.3, a hardcoded BETTER_AUTH_SECRET fallback ("better-auth-secret-123456789") lets an unauthenticated attacker forge email verification JWTs, trigger auto-sign-in as admin, and execute commands on the host via the built-in SSH terminal. This vulnerability is fixed in 0.29.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45631.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-w3gm-rc4p-9rhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45631
- https://github.com/Dokploy/dokploy/pull/4374
