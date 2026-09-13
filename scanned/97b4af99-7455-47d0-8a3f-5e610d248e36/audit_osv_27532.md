# [H] SQL Injection in PostgreSQL Anonymizer 1.2 allows table owner to gain superuser privileges via masking rule

## Summary
Severity: High
Advisory: CVE-2024-2338
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-08
Source: https://osv.dev/vulnerability/CVE-2024-2338
Type: osv

## Details
PostgreSQL Anonymizer v1.2 contains a SQL injection vulnerability that allows a user who owns a table to elevate to superuser when dynamic masking is enabled. PostgreSQL Anonymizer enables users to set security labels on tables to mask specified columns. There is a flaw that allows complex expressions to be provided as a value. This expression is then later used as it to create the masked views leading to SQL Injection. If dynamic masking is enabled, this will lead to privilege escalation to superuser after the label is created. Users that don't own a table, especially masked users cannot exploit this vulnerability. The problem is resolved in v1.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2338.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2338
- https://gitlab.com/dalibo/postgresql_anonymizer/-/commit/f55daadba3fa8226029687964aa8889d01a79778
