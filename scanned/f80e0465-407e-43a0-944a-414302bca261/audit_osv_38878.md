# [C] SOCFortress CoPilot: Hardcoded JWT secret allows unauthenticated full admin compromise and lateral movement into all integrated SOC tools

## Summary
Severity: Critical
Advisory: CVE-2026-42869
Aliases: GHSA-4gxj-hw3c-3x2x
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-42869
Type: osv

## Details
SOCFortress CoPilot focuses on providing a single pane of glass for all your security operations needs. Prior to 0.1.57, SOCFortress CoPilot ships a hardcoded JWT signing secret as a fallback value in backend/app/auth/utils.py:28 and ships it verbatim in .env.example. Any deployment where JWT_SECRET is not explicitly set — including the default Docker Compose setup — signs all authentication tokens with this publicly known value. An unauthenticated attacker can forge arbitrary admin-scoped JWTs and gain full control of the application and every security tool it manages without any credentials. This vulnerability is fixed in 0.1.57.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42869.json
- https://github.com/socfortress/CoPilot/security/advisories/GHSA-4gxj-hw3c-3x2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-42869
- https://github.com/socfortress/CoPilot/commit/4640511a0cf2e7b144a71375b5b349a8318cb186
- https://github.com/socfortress/CoPilot/pull/814
