# [M] Multiple SQL injections in sql/instance.py param_edit method in Archery - GHSL-2022-104

## Summary
Severity: Medium
Advisory: CVE-2023-30605
Aliases: GHSA-6mqc-w2qp-fvhp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30605
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases. User input coming from the `variable_name` and `variable_value` parameter value in the `sql/instance.py` `param_edit` endpoint is passed to a set of methods in given SQL engine implementations, which concatenate user input unsafely into a SQL query and afterwards pass it to the `query` method of each database engine for execution. The affected methods are: `set_variable` in `sql/engines/goinception.py` which concatenates input which is passed to execution on the database in the `sql/engines/goinception.py`, `get_variables` in `sql/engines/goinception.py`  which concatenates input which is passed to execution on the database in the `sql/engines/goinception.py`, `set_variable` in `sql/engines/mysql.py`  which concatenates input which is passed to execution on the database in the `sql/engines/mysql.py` `query`, and `get_variables` in `sql/engines/mysql.py`which concatenates input which is passed to execution on the database in the `sql/engines/mysql.py` `query`. Each of these issues may be mitigated by escaping user input or by using prepared statements when executing SQL queries. This advisory is also indexed as `GHSL-2022-104`.

## References
- https://github.com/hhyo/Archery/blob/bc86cda4c3b7d59f759d0d23bb63a54f52616752/sql/instance.py#L161-L202
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30605.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-6mqc-w2qp-fvhp
- https://nvd.nist.gov/vuln/detail/CVE-2023-30605
