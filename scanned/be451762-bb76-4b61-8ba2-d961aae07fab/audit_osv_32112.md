# [C] SQL Injection in Mattermost Boards via board category ID reordering

## Summary
Severity: Critical
Advisory: CVE-2025-24490
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-02-24
Source: https://osv.dev/vulnerability/CVE-2025-24490
Type: osv

## Details
Mattermost versions 10.4.x <= 10.4.1, 9.11.x <= 9.11.7, 10.3.x <= 10.3.2, 10.2.x <= 10.2.2 fail to use prepared statements in the SQL query of boards reordering which allows an attacker to retrieve data from the database, via a SQL injection when reordering specially crafted boards categories.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24490.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-24490
