# [C] ArcadeDB before 26.7.3 Privilege Escalation via JavaScript Trigger

## Summary
Severity: Critical
Advisory: CVE-2026-67356
Aliases: GHSA-38pf-6hp2-pxww
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-02
Source: https://osv.dev/vulnerability/CVE-2026-67356
Type: osv

## Details
ArcadeDB before 26.7.3 binds the real LocalDatabase object into JavaScript trigger contexts with HostAccess.ALL, allowing schema-admins to call getSecurity().createUser() without permission checks. Attackers with UPDATE_SCHEMA permission can create triggers that execute JavaScript to create server-wide admin users, escalating privileges beyond their authorization level.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-38pf-6hp2-pxww
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67356.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67356
- https://www.vulncheck.com/advisories/arcadedb-before-privilege-escalation-via-javascript-trigger
