# [M] Apache Hive Code Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vpw3-3prf-3974
CVE: CVE-2023-35701
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-vpw3-3prf-3974
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-jdbc` — affected >=4.0.0-alpha-1 <4.0.0

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Apache Hive.

The vulnerability affects the Hive JDBC driver component and it can potentially lead to arbitrary code execution on the machine/endpoint that the JDBC driver (client) is running. The malicious user must have sufficient permissions to specify/edit JDBC URL(s) in an endpoint relying on the Hive JDBC driver and the JDBC client process must run under a privileged user to fully exploit the vulnerability. 

The attacker can setup a malicious HTTP server and specify a JDBC URL pointing towards this server. When a JDBC connection is attempted, the malicious HTTP server can provide a special response with customized payload that can trigger the execution of certain commands in the JDBC client.This issue affects Apache Hive: from 4.0.0-alpha-1 before 4.0.0.

Users are recommended to upgrade to version 4.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35701
- https://github.com/apache/hive/commit/7abeb1df463cc389f668172e7cf3bb772799858a
- https://github.com/apache/hive
- https://issues.apache.org/jira/browse/HIVE-27554
- https://lists.apache.org/thread/7zcv6l63spl4r66xwz5jv9rtrg2opx81
- http://www.openwall.com/lists/oss-security/2024/05/03/3
