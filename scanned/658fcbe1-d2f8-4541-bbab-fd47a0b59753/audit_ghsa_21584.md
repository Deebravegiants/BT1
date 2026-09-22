# [M] snowflake-connector-python is vulnerable to Regular Expression Denial of Service (ReDoS)

## Summary
Severity: Medium
Advisory: GHSA-4r6j-fwcx-94cf
CVE: CVE-2022-42965
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-4r6j-fwcx-94cf
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=0 <2.8.2

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the snowflake-connector-python PyPI package, when an attacker is able to supply arbitrary input to the get_file_transfer_type method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42965
- https://github.com/snowflakedb/snowflake-connector-python/pull/1327
- https://github.com/snowflakedb/snowflake-connector-python/commit/b9d2fc789fae4db865dde3d2a1bd72c8a9eab091
- https://github.com/snowflakedb/snowflake-connector-python
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v2.8.2
- https://research.jfrog.com/vulnerabilities/snowflake-connector-python-redos-xray-257185
