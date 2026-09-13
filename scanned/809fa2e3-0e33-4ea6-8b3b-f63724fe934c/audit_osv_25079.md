# [M] Multiple SQL injections in sql/data_dictionary.py table_list method in Archery - GHSL-2022-105

## Summary
Severity: Medium
Advisory: CVE-2023-30558
Aliases: GHSA-jwjj-jgfv-x66q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30558
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases. User input coming from the `db_name` in the `sql/data_dictionary.py` `table_list` endpoint is passed to the methods that follow in a given SQL engine implementations, which concatenate user input unsafely into a SQL query and afterwards pass it to the `query` method of each database engine for execution. The affected methods are `get_group_tables_by_db` in `sql/engines/mssql.py`which passes unsafe user input to `sql/engines/mssql.py`, and `get_group_tables_by_db` in `sql/engines/oracle.py`which concatenates input which is passed to execution on the database in the `sql/engines/oracle.py` `query` method. Each of these issues may be mitigated by escaping user input or by using prepared statements when executing SQL queries. This issue is also indexed as `GHSL-2022-105`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30558.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-jwjj-jgfv-x66q
- https://nvd.nist.gov/vuln/detail/CVE-2023-30558
