# [M] CVE-2025-55476

## Summary
Severity: Medium
Advisory: CVE-2025-55476
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-55476
Type: osv

## Details
FireShare FileShare 1.2.25 contains a time-based blind SQL injection vulnerability in the sort parameter of the endpoint: GET /api/videos/public?sort= This parameter is unsafely evaluated in a SQL ORDER BY clause without proper sanitization, allowing an attacker to inject arbitrary SQL subqueries.

## References
- https://cyber-ducky.com/blind-sql-injection-in-fireshare-found-in-an-api-sort-parameter/
- https://github.com/ShaneIsrael/fireshare/releases/tag/v1.2.26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55476.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55476
- https://github.com/ShaneIsrael/fireshare/issues/311
