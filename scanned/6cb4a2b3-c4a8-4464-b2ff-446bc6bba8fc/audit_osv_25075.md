# [M] SQL injection in sql_api/api_workflow.py endpoint in Archery - GHSL-2022-103

## Summary
Severity: Medium
Advisory: CVE-2023-30554
Aliases: GHSA-3p43-89m6-7x5w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30554
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases. Affected versions are subject to SQL injection in the `sql_api/api_workflow.py` endpoint `ExecuteCheck` which passes unfiltered input to the `explain_check` method in `sql/engines/oracle.py`. User input coming from the `db_name` parameter value in the `api_workflow.py` `ExecuteCheck` endpoint is passed through the `oracle.py` `execute_check` method and to the `explain_check` method for execution. Each of these issues may be mitigated by escaping user input or by using prepared statements when executing SQL queries. This issue is also indexed as `GHSL-2022-103`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30554.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-3p43-89m6-7x5w
- https://nvd.nist.gov/vuln/detail/CVE-2023-30554
