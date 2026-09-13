# [M] Infinite Loop in Apache Xerces Java

## Summary
Severity: Medium
Advisory: GHSA-h65f-jvqw-m9fj
CVE: CVE-2022-23437
CWE: CWE-91
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-h65f-jvqw-m9fj
Type: github-advisory

## Affected
- Maven: `xerces:xercesImpl` — affected >=0 <2.12.2

## Details
There's a vulnerability within the Apache Xerces Java (XercesJ) XML parser when handling specially crafted XML document payloads. This causes, the XercesJ XML parser to wait in an infinite loop, which may sometimes consume system resources for prolonged duration. This vulnerability is present within XercesJ version 2.12.1 and the previous versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23437
- https://github.com/jboss/xerces
- https://lists.apache.org/thread/6pjwm10bb69kq955fzr1n0nflnjd27dl
- https://security.netapp.com/advisory/ntap-20221028-0005
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2022/01/24/3
