# [C] Budibase before 3.40.0 SQL Injection via Oracle connector

## Summary
Severity: Critical
Advisory: CVE-2026-72853
Aliases: GHSA-xj29-x47g-9w2c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72853
Type: osv

## Details
Budibase before 3.40.0 contains a SQL injection vulnerability in the Oracle datasource connector's post-write row lookup that fails to escape table names in identifiers. Attackers with write permission on a table with a double-quote in its name can inject SQL that executes as the datasource's database user to read or modify arbitrary data.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-xj29-x47g-9w2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72853.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72853
- https://www.vulncheck.com/advisories/budibase-before-sql-injection-via-oracle-connector
