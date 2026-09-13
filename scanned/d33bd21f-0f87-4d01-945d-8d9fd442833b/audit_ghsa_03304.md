# [H] Deserialization of Untrusted Data in Apache Camel RabbitMQ

## Summary
Severity: High
Advisory: GHSA-2x6r-7427-95cm
CVE: CVE-2020-11972
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-2x6r-7427-95cm
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-rabbitmq` — affected >=0 <2.25.1
- Maven: `org.apache.camel:camel-rabbitmq` — affected >=3.0.0 <3.2.0

## Details
Apache Camel RabbitMQ enables Java deserialization by default. Apache Camel 2.22.x, 2.23.x, 2.24.x, 2.25.0, 3.0.0 up to 3.1.0 are affected. 2.x users should upgrade to 2.25.1, 3.x users should upgrade to 3.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11972
- https://camel.apache.org/security/CVE-2020-11972.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://www.openwall.com/lists/oss-security/2020/05/14/10
- http://www.openwall.com/lists/oss-security/2020/05/14/8
