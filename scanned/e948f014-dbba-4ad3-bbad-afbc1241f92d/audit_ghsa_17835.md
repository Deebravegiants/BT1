# [M] snowflake-connector-python vulnerable to insecure deserialization of the OCSP response cache

## Summary
Severity: Medium
Advisory: GHSA-m4f6-vcj4-w5mx
CVE: CVE-2025-24794
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-m4f6-vcj4-w5mx
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=2.7.12 <3.13.1

## Details
### Issue
Snowflake discovered and remediated a vulnerability in the Snowflake Connector for Python. The OCSP response cache uses pickle as the serialization format, potentially leading to local privilege escalation.

This vulnerability affects versions 2.7.12 through 3.13.0. Snowflake fixed the issue in version 3.13.1.

### Vulnerability Details
The OCSP response cache is saved locally on the machine running the Connector using the pickle serialization format. This can potentially lead to local privilege escalation if an attacker has write access to the OCSP response cache file.

### Solution
Snowflake released version 3.13.1 of the Snowflake Connector for Python, which fixes this issue. We recommend users upgrade to version 3.13.1.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-python/security/advisories/GHSA-m4f6-vcj4-w5mx
- https://nvd.nist.gov/vuln/detail/CVE-2025-24794
- https://github.com/snowflakedb/snowflake-connector-python/commit/3769b43822357c3874c40f5e74068458c2dc79af
- https://github.com/pypa/advisory-database/tree/main/vulns/snowflake-connector-python/PYSEC-2025-27.yaml
- https://github.com/snowflakedb/snowflake-connector-python
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v3.13.1
