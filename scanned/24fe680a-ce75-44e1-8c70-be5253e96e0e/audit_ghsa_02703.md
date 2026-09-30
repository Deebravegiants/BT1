# [C] Security check skip in Apache Dubbo

## Summary
Severity: Critical
Advisory: GHSA-q897-9jxf-jg9r
CVE: CVE-2021-37579
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-10
Source: https://github.com/advisories/GHSA-q897-9jxf-jg9r
Type: github-advisory

## Affected
- Maven: `org.apache.dubbo:dubbo` — affected >=0 <2.7.13
- Maven: `org.apache.dubbo:dubbo` — affected >=3.0.0 <3.0.2

## Details
The Dubbo Provider will check the incoming request and the corresponding serialization type of this request meet the configuration set by the server. But there's an exception that the attacker can use to skip the security check (when enabled) and reaching a deserialization operation with native java serialization. Apache Dubbo 2.7.13, 3.0.2 fixed this issue by quickly fail when any unrecognized request was found.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-37579
- https://github.com/apache/dubbo
- https://lists.apache.org/thread.html/r898afa109cdbb4b79724308648ff0718152ebe1d3d6dfc7202d958bc%40%3Cdev.dubbo.apache.org%3E
