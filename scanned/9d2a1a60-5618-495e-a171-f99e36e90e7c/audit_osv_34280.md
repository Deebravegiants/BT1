# [M] CVE-2025-57423

## Summary
Severity: Medium
Advisory: CVE-2025-57423
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-57423
Type: osv

## Details
A SQL injection vulnerability was discovered in the /articles endpoint of MyClub 0.5, affecting the query parameters Content, GroupName, PersonName, lastUpdate, pool, and title. Due to insufficient input sanitisation, an unauthenticated remote attacker could inject arbitrary SQL commands via a crafted GET request, potentially leading to information disclosure or manipulation of the database.

## References
- https://aardwolfsecurity.com/cve-2025-57423-critical-sql-injection-in-myclub/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57423.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57423
- https://github.com/jebissey/MyClub/issues/2
- https://github.com/jebissey/MyClub/commit/5741f39cf02215d3d01bf98f6133ac53d27e1556
- https://github.com/jebissey/MyClub/commit/f067bb63ac7df153e95565529d99ac35de2c347e
