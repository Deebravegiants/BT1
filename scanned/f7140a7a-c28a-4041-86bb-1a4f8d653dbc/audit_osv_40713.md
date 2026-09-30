# [M] Wallos: Unauthenticated database replacement via import endpoint on fresh install

## Summary
Severity: Medium
Advisory: CVE-2026-54600
Aliases: GHSA-8wqc-r9j3-rv7m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-54600
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.9.4, endpoints/db/import.php has no authentication. The only guard is a user-table row count — if zero (fresh/unconfigured install), an unauthenticated attacker can replace the entire database. This issue has been patched in version 4.9.4.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.9.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54600.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-8wqc-r9j3-rv7m
- https://nvd.nist.gov/vuln/detail/CVE-2026-54600
