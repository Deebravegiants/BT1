# [M] The Snowflake Connector for Python stores sensitive data in logs

## Summary
Severity: Medium
Advisory: GHSA-5vvg-pvhp-hv2m
CVE: CVE-2024-49750
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-5vvg-pvhp-hv2m
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=0 <3.12.3

## Details
### Issue
Snowflake recently learned about and remediated a set of vulnerabilities in the Snowflake Connector for Python. Under specific conditions, certain users credentials (or portions of those credentials) were logged locally by the Connector to the users own systems. The credentials were not logged by Snowflake.

These vulnerabilities affect versions up to and including 3.12.2. Snowflake fixed the issue in version 3.12.3.

### Vulnerability Details
When the logging level was set by the user to DEBUG, the Connector could have logged Duo passcodes (when specified via the “passcode” parameter) and Azure SAS tokens. Additionally, the [SecretDetector](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example#logging) logging formatter, if enabled, contained bugs which caused it to not fully redact JWT tokens and certain private key formats.

### Solution
Snowflake released version 3.12.3 of the Snowflake Connector for Python, which fixes these issues. We recommend users upgrade to version 3.12.3 and review their logs for any potentially sensitive information that may have been captured.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-python/security/advisories/GHSA-5vvg-pvhp-hv2m
- https://nvd.nist.gov/vuln/detail/CVE-2024-49750
- https://github.com/snowflakedb/snowflake-connector-python/commit/dbc9284a3c0382c131b971b35e8d6ab93c46f37a
- https://github.com/pypa/advisory-database/tree/main/vulns/snowflake-connector-python/PYSEC-2024-191.yaml
- https://github.com/snowflakedb/snowflake-connector-python
