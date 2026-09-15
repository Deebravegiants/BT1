# [M] Snowflake JDBC uses insecure temporary credential cache file permissions

## Summary
Severity: Medium
Advisory: GHSA-33g6-495w-v8j2
CVE: CVE-2025-24790
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-33g6-495w-v8j2
Type: github-advisory

## Affected
- Maven: `net.snowflake:snowflake-jdbc` — affected >=3.6.8 <3.22.0

## Details
### Issue
Snowflake discovered and remediated a vulnerability in the Snowflake JDBC Driver. On Linux systems, when temporary credential caching is enabled, the Snowflake JDBC Driver will cache temporary credentials locally in a world-readable file.

This vulnerability affects versions 3.6.8 through 3.21.0. Snowflake fixed the issue in version 3.22.0.

### Vulnerability Details
On Linux, when either EXTERNALBROWSER or USERNAME_PASSWORD_MFA authentication methods are used with temporary credential caching enabled, the Snowflake JDBC Driver will cache temporary credentials in a local file. In the vulnerable versions of the Driver, this file is created with world-readable permissions.

### Solution
Snowflake released version 3.22.0 of the Snowflake JDBC Driver, which fixes this issue. We recommend users upgrade to version 3.22.0.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-jdbc/security/advisories/GHSA-33g6-495w-v8j2
- https://nvd.nist.gov/vuln/detail/CVE-2025-24790
- https://github.com/snowflakedb/snowflake-jdbc/commit/9e1a5acf12406b16c4780ca013f4c4db48b74b59
- https://github.com/snowflakedb/snowflake-jdbc
