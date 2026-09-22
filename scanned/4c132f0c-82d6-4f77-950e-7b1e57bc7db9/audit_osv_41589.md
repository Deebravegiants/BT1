# [H] clawvet < 0.7.5 Hard-coded JWT Secret Session Forgery

## Summary
Severity: High
Advisory: CVE-2026-62241
Aliases: GHSA-9mww-p953-jfc9
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-62241
Type: osv

## Details
clawvet self-hosted API server (apps/api) before 0.7.5 hard-codes a fallback JWT secret ('clawvet-dev-secret-change-me') in auth.ts and ships it as the default in .env.example. Because GET /api/v1/scans returns scan records containing userId values without authentication, a remote unauthenticated attacker can harvest a victim's userId, forge a valid HS256 cg_session cookie offline using the known secret, and call GET /api/v1/auth/me to obtain the victim's email address, subscription plan, and secret apiKey. The published clawvet npm package (CLI only) is not affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62241.json
- https://github.com/MohibShaikh/clawvet/security/advisories/GHSA-9mww-p953-jfc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-62241
- https://www.vulncheck.com/advisories/clawvet-hard-coded-jwt-secret-session-forgery
- https://github.com/MohibShaikh/clawvet
