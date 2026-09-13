# [H] snowflake-connector-python vulnerable to SQL Injection in write_pandas

## Summary
Severity: High
Advisory: GHSA-2vpq-fh52-j3wv
CVE: CVE-2025-24793
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-2vpq-fh52-j3wv
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=2.2.5 <3.13.1

## Details
### Issue
Snowflake discovered and remediated a vulnerability in the Snowflake Connector for Python. A function from the snowflake.connector.pandas_tools module is vulnerable to SQL injection.

This vulnerability affects versions 2.2.5 through 3.13.0. Snowflake fixed the issue in version 3.13.1.

### Vulnerability Details
A function from the snowflake.connector.pandas_tools module is not sanitizing all of its arguments, and queries using them are not parametrized. An attacker controlling these arguments could achieve SQL injection by passing crafted input. Any SQL executed that way by an attacker would still run in the context of the current session.

### Solution
Snowflake released version 3.13.1 of the Snowflake Connector for Python, which fixes this issue. We recommend users upgrade to version 3.13.1.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-python/security/advisories/GHSA-2vpq-fh52-j3wv
- https://nvd.nist.gov/vuln/detail/CVE-2025-24793
- https://github.com/snowflakedb/snowflake-connector-python/commit/f3f9b666518d29c31a49384bbaa9a65889e72056
- https://github.com/pypa/advisory-database/tree/main/vulns/snowflake-connector-python/PYSEC-2025-26.yaml
- https://github.com/snowflakedb/snowflake-connector-python
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v3.13.1
