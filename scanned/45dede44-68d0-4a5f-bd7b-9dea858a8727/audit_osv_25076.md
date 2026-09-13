# [M] SQL injection in sql_optimize.py explain method in Archery - GHSL-2022-108

## Summary
Severity: Medium
Advisory: CVE-2023-30555
Aliases: GHSA-349r-2663-cr3w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30555
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases.Affected versions are subject to SQL injection in the `explain` method in `sql_optimize.py`. User input coming from the `db_name` parameter value in the `explain` endpoint is passed to the following `query` methods of each database engine for execution. `query` in `sql/engines/mssql.py`, and `query` in `sql/engines/oracle.py`. Each of these issues may be mitigated by escaping user input or by using prepared statements when executing SQL queries. This issue is also indexed as `GHSL-2022-108`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30555.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-349r-2663-cr3w
- https://nvd.nist.gov/vuln/detail/CVE-2023-30555
