# [M] snowflake-connector-python vulnerable to insecure cache files permissions

## Summary
Severity: Medium
Advisory: GHSA-r2x6-cjg7-8r43
CVE: CVE-2025-24795
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-r2x6-cjg7-8r43
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=2.3.7 <3.13.1

## Details
### Issue
Snowflake discovered and remediated a vulnerability in the Snowflake Connector for Python. On Linux systems, when temporary credential caching is enabled, the Snowflake Connector for Python will cache temporary credentials locally in a world-readable file.

This vulnerability affects versions 2.3.7 through 3.13.0. Snowflake fixed the issue in version 3.13.1.

### Vulnerability Details
On Linux, when either EXTERNALBROWSER or USERNAME_PASSWORD_MFA authentication methods are used with temporary credential caching enabled, the Snowflake Connector for Python will cache the temporary credentials in a local file. In the vulnerable versions of the Driver, this file is created with world-readable permissions.

### Solution
Snowflake released version 3.13.1 of the Snowflake Connector for Python, which fixes this issue. We recommend users upgrade to version 3.13.1.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-python/security/advisories/GHSA-r2x6-cjg7-8r43
- https://nvd.nist.gov/vuln/detail/CVE-2025-24795
- https://github.com/snowflakedb/snowflake-connector-python/commit/3769b43822357c3874c40f5e74068458c2dc79af
- https://github.com/pypa/advisory-database/tree/main/vulns/snowflake-connector-python/PYSEC-2025-28.yaml
- https://github.com/snowflakedb/snowflake-connector-python
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v3.13.1
