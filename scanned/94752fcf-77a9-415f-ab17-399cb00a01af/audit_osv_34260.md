# [M] Cursor allows PostgreSQL Anonymizer masked user to gain unauthorized access to authentic data

## Summary
Severity: Medium
Advisory: CVE-2025-5690
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-04
Source: https://osv.dev/vulnerability/CVE-2025-5690
Type: osv

## Details
PostgreSQL Anonymizer v2.0 and v2.1 contain a vulnerability that allows a masked user to bypass the masking rules defined on a table and read the original data using a database cursor or the --insert option of pg_dump. This problem occurs only when dynamic masking is enabled, which is not the default setting. The problem is resolved in version 2.2.1

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5690.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5690
- https://gitlab.com/dalibo/postgresql_anonymizer/-/issues/531
