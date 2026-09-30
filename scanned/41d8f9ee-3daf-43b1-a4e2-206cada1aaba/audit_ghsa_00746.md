# [C] dom4j allows External Entities by default which might enable XXE attacks

## Summary
Severity: Critical
Advisory: GHSA-hwj3-m3p6-hj38
CVE: CVE-2020-10683
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-hwj3-m3p6-hj38
Type: github-advisory

## Affected
- Maven: `org.dom4j:dom4j` — affected >=0 <2.0.3
- Maven: `org.dom4j:dom4j` — affected >=2.1.0 <2.1.3
- Maven: `dom4j:dom4j` — affected >=0

## Details
dom4j before 2.1.3 allows external DTDs and External Entities by default, which might enable XXE attacks. However, there is popular external documentation from OWASP showing how to enable the safe, non-default behavior in any application that uses dom4j.

Note: This advisory applies to `dom4j:dom4j` version 1.x legacy artifacts.  To resolve this a change to the latest version of `org.dom4j:dom4j` is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10683
- https://github.com/dom4j/dom4j/issues/87
- https://github.com/dom4j/dom4j/commit/1707bf3d898a8ada3b213acb0e3b38f16eaae73d
- https://github.com/dom4j/dom4j/commit/a8228522a99a02146106672a34c104adbda5c658
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://usn.ubuntu.com/4575-1
- https://security.netapp.com/advisory/ntap-20200518-0002
- https://lists.apache.org/thread.html/rb1b990d7920ae0d50da5109b73b92bab736d46c9788dd4b135cb1a51@%3Cnotifications.freemarker.apache.org%3E
- https://lists.apache.org/thread.html/r91c64cd51e68e97d524395474eaa25362d564572276b9917fcbf5c32@%3Cdev.velocity.apache.org%3E
- https://lists.apache.org/thread.html/r51f3f9801058e47153c0ad9bc6209d57a592fc0e7aefd787760911b8@%3Cdev.velocity.apache.org%3E
- https://github.com/dom4j/dom4j/releases/tag/version-2.1.3
- https://github.com/dom4j/dom4j/commits/version-2.0.3
- https://github.com/dom4j/dom4j
