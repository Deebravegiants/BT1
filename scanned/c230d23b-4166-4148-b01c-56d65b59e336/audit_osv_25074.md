# [M] Multiple SQL injections in sql_api/api_workflow.py endpoint in Archery - GHSL-2022-102

## Summary
Severity: Medium
Advisory: CVE-2023-30553
Aliases: GHSA-hvcq-r2r2-34ch
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30553
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases. Affected versions are subject to multiple SQL injections in the `sql_api/api_workflow.py` endpoint `ExecuteCheck`. User input coming from the `db_name` parameter value and the `full_sql` parameter value in the `api_workflow.py` `ExecuteCheck` endpoint is passed to the methods that follow in given SQL engine implementations, which concatenate user input unsafely into a SQL query and afterwards pass it to the `query` method of each database engine for execution. The affected methods are `execute_check` in `sql/engines/clickhouse.py` which concatenates input which is passed to execution on the database in the `sql/engines/clickhouse.py` `query` method, `execute_check` in `sql/engines/goinception.py`which concatenates input which is passed to execution on the database in the `sql/engines/goinception.py` `query` method, `execute_check` in `sql/engines/oracle.py`which passes unsafe user input into the `object_name_check` method in `sql/engines/oracle.py` which in turn is passed to execution on the database in the `sql/engines/oracle.py` `query` method. Each of these issues may be mitigated by escaping user input or by using prepared statements when executing SQL queries. This issue is also indexed as `GHSL-2022-102`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30553.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-hvcq-r2r2-34ch
- https://nvd.nist.gov/vuln/detail/CVE-2023-30553
