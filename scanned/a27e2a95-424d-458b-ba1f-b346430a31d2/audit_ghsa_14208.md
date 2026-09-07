# [H] Snowflake JDBC vulnerable to command injection via SSO URL authentication

## Summary
Severity: High
Advisory: GHSA-4g3j-c4wg-6j7x
CVE: CVE-2023-30535
CWE: CWE-20, CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-14
Source: https://github.com/advisories/GHSA-4g3j-c4wg-6j7x
Type: github-advisory

## Affected
- Maven: `net.snowflake:snowflake-jdbc` — affected >=0 <3.13.29

## Details
Snowflake JDBC driver is vulnerable to command injection vulnerability via SSO URL authentication. The vulnerability was patched on March 17, 2023 as part of Snowflake JDBC driver Version 3.13.29. An attacker could set up a malicious, publicly accessible server which responds to the SSO URL with an attack payload. If the attacker then tricked a user into visiting the maliciously crafted connection URL, the user’s local machine would render the malicious payload, leading to a remote code execution.

## References
- https://github.com/snowflakedb/snowflake-jdbc/security/advisories/GHSA-4g3j-c4wg-6j7x
- https://nvd.nist.gov/vuln/detail/CVE-2023-30535
- https://community.snowflake.com/s/article/JDBC-Driver-Release-Notes
- https://github.com/snowflakedb/snowflake-jdbc
