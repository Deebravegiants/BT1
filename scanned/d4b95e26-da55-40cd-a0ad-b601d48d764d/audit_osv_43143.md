# [C] Tencent APIJSON - Unauthenticated SQL Injection via @having Operator Map-Form Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-72565
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72565
Type: osv

## Details
A SQL injection vulnerability in Tencent APIJSON through 8.1.8 allows unauthenticated remote attackers to bypass per-table access control and read arbitrary database tables via the Map-form @having operator.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72565.json
- https://github.com/Tencent/APIJSON
- https://nvd.nist.gov/vuln/detail/CVE-2026-72565
- https://github.com/Tencent/APIJSON/blob/master/APIJSONORM/src/main/java/apijson/orm/AbstractSQLConfig.java
