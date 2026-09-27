# [M] SQL injection in data_dictionary.py table_info method in Archery - GHSL-2022-106

## Summary
Severity: Medium
Advisory: CVE-2023-30557
Aliases: GHSA-9pvw-f8jv-xxjr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30557
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases. Affected versions are subject to SQL injection in the `data_dictionary.py` `table_info`. User input coming from the `db_name` in and the `tb_name` parameter values in the `sql/data_dictionary.py` `table_info` endpoint is passed to the following methods in the given SQL engine implementations, which concatenate user input unsafely into a SQL query and afterwards pass it to the `query` method of each database engine for execution.The methods are `get_table_meta_data ` in `sql/engines/mssql.py` which passes unsafe user input to the `sql/engines/mssql.py` `query` method, `get_table_desc_data` in `sql/engines/mssql.py`which passes unsafe user input to the `sql/engines/mssql.py` `query`, `get_table_index_data` in `sql/engines/mssql.py`which passes unsafe user input to the `sql/engines/mssql.py` `query` method, `get_table_meta_data` in `sql/engines/oracle.py`which concatenates input which is passed to execution on the database in the `sql/engines/oracle.py` `query` method, `get_table_desc_data` in `sql/engines/oracle.py`which concatenates input which is passed to execution on the database in the `sql/engines/oracle.py` `query` method, and `get_table_index_data` in `sql/engines/oracle.py` which concatenates input which is passed to execution on the database in the `sql/engines/oracle.py` `query` method. Each of these issues may be mitigated by escaping user input or by using prepared statements when executing SQL queries. This issue is also indexed as `GHSL-2022-106`.

## References
- https://github.com/hhyo/Archery/blob/bc86cda4c3b7d59f759d0d23bb63a54f52616752/sql/data_dictionary.py#L47-L86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30557.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-9pvw-f8jv-xxjr
- https://nvd.nist.gov/vuln/detail/CVE-2023-30557
