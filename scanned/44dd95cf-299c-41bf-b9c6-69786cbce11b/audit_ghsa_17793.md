# [H] Snowflake JDBC allows an untrusted search path on Windows

## Summary
Severity: High
Advisory: GHSA-7hpq-3g6w-pvhf
CVE: CVE-2025-24789
CWE: CWE-426
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-7hpq-3g6w-pvhf
Type: github-advisory

## Affected
- Maven: `net.snowflake:snowflake-jdbc` — affected >=3.2.3 <3.22.0

## Details
### Issue
Snowflake discovered and remediated a vulnerability in the Snowflake JDBC Driver. When the EXTERNALBROWSER authentication method is used on Windows, an attacker with write access to a directory in the %PATH% can escalate their privileges to the user that runs the vulnerable JDBC Driver version.

This vulnerability affects versions 3.2.3 through 3.21.0 on Windows. Snowflake fixed the issue in version 3.22.0.

### Vulnerability Details
When the EXTERNALBROWSER authentication method is selected, the Snowflake JDBC Driver on non-macOS operating systems tries to open the SSO URL using xdg-open. Because xdg-open is a Linux program that doesn’t exist in a default Windows installation, a sufficiently privileged attacker could place a malicious executable in one of the directories on the %PATH% and achieve local privilege escalation to the user running the JDBC Driver.

### Solution
Snowflake released version 3.22.0 of the Snowflake JDBC Driver, which fixes this issue. We recommend users upgrade to version 3.22.0.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-jdbc/security/advisories/GHSA-7hpq-3g6w-pvhf
- https://nvd.nist.gov/vuln/detail/CVE-2025-24789
- https://github.com/snowflakedb/snowflake-jdbc/commit/4f01bb8f9b708c71e7a2111c87371dbfc1d53dd6
- https://github.com/snowflakedb/snowflake-jdbc
