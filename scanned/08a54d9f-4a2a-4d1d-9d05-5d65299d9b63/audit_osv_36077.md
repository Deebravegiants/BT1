# [H] Baserow 2.3.3 - SQL injection in formula index() JSONB array extraction

## Summary
Severity: High
Advisory: CVE-2026-19754
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-19754
Type: osv

## Details
Baserow 2.3.3 contains a SQL injection vulnerability in the index() formula function. A low-privileged authenticated user who can create or modify formula fields can provide an undocumented fourth argument that is treated as a SQL template and interpolated directly into a PostgreSQL expression.



The vulnerable expression is executed when Baserow recalculates formula field values. Because the generated SQL runs through Baserow's database connection, the injected SQL executes with the privileges of the Baserow PostgreSQL role rather than the permissions of the authenticated application user.



This issue affects Baserow: 2.3.3.

## References
- https://fluidattacks.com/es/advisories/superestrella
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19754.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19754
- https://github.com/baserow/baserow
