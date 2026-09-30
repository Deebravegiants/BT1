# [M] CVE-2025-55472

## Summary
Severity: Medium
Advisory: CVE-2025-55472
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-55472
Type: osv

## Details
SQL Injection vulnerability exists in Tirreno v0.9.5, specifically in the /admin/loadUsers API endpoint. The vulnerability arises due to unsafe handling of user-supplied input in the columns[0][data] parameter, which is directly used in SQL queries without proper validation or parameterization.

## References
- https://cyberducky.medium.com/blind-sql-injection-found-in-tirreno-security-analytics-cbd791cec1c0
- https://github.com/tirrenotechnologies/tirreno/releases/tag/v0.9.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55472.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55472
- https://github.com/tirrenotechnologies/tirreno
