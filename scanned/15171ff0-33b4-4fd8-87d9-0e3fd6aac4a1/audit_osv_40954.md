# [H] Apache Fineract: Boolean SQL Injection in Client Search API (orderBy parameter) leading to Local File Disclosure

## Summary
Severity: High
Advisory: CVE-2026-56287
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-56287
Type: osv

## Details
A boolean-based SQL Injection vulnerability exists in Apache Fineract's Client Search API (GET /api/v1/clients) in versions up to and including 1.14.0. The orderBy and sortOrder request parameters are concatenated into a SQL query without sufficient validation, allowing an authenticated user with permission to view clients to inject arbitrary SQL via a crafted orderBy value. This can be leveraged to perform blind boolean-based data extraction and, on MySQL/MariaDB, to disclose arbitrary files readable by the database process via the LOAD_FILE() function. Users are recommended to upgrade to a version containing the fix

## References
- http://www.openwall.com/lists/oss-security/2026/07/15/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56287.json
- https://lists.apache.org/thread/l5klcj2v0dx63bssvb0gmw1nzzc47col
- https://nvd.nist.gov/vuln/detail/CVE-2026-56287
- https://github.com/apache/fineract/pull/6020
