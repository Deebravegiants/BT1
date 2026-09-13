# [H] Multiple SQL/DDL Injection and Arbitrary File Read Vulnerabilities in snowflake-sqlalchemy

## Summary
Severity: High
Advisory: CVE-2026-15736
Aliases: GHSA-8g6f-qw9x-4q6q, PYSEC-2026-3921
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-15736
Type: osv

## Details
Snowflake SQLAlchemy versions prior to 1.11.0 contain several security vulnerabilities, including: Improper handling of user-supplied column identifiers in merge operations could allow SQL injection through attacker-controlled input keys. An attacker may be able to exploit this through request field names in a dynamic upsert endpoint, potentially enabling read access to data visible to the application's database role or modification of values within the same MERGE statement. Improper literal rendering of bound parameters when building certain Snowflake-specific table creation queries could allow SQL injection. An attacker may be able to exploit this by supplying a crafted string to any application endpoint that passes user-controlled data through the affected query-building API, potentially causing arbitrary data exfiltration within the scope of the connection role. Improper forwarding of connection configuration parameters could allow an attacker to cause the library to read arbitrary local files and transmit their contents to an attacker-controlled endpoint. An attacker may be able to exploit this in deployment environments that accept user-controlled connection parameters, potentially exposing sensitive files accessible to the application process. The fix is available in Snowflake SQLAlchemy version 1.11.0. Users must manually upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15736.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15736
- https://github.com/snowflakedb/snowflake-sqlalchemy/releases
