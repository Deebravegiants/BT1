# [M] Cross-site Scripting in healthcheck webconsole plugin

## Summary
Severity: Medium
Advisory: GHSA-4pvw-g9fx-594r
CVE: CVE-2023-38435
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-4pvw-g9fx-594r
Type: github-advisory

## Affected
- Maven: `org.apache.felix:org.apache.felix.healthcheck.webconsoleplugin` — affected >=0 <2.1.0

## Details
An improper neutralization of input during web page generation ('Cross-site Scripting') [CWE-79] vulnerability in Apache Felix Healthcheck Webconsole Plugin version 2.0.2 and prior may allow an attacker to perform a reflected cross-site scripting (XSS) attack.

Upgrade to Apache Felix Healthcheck Webconsole Plugin 2.1.0 or higher.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38435
- https://github.com/apache/felix-dev/commit/c4e67520e0a4499389342491869919a6c42ed62c
- https://github.com/apache/felix-dev
- https://lists.apache.org/thread/r3blhp3onr4rdbkgdyglqnccg0v79pfv
- http://seclists.org/fulldisclosure/2023/Jul/43
- http://www.openwall.com/lists/oss-security/2023/07/25/10
