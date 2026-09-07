# [H] Apache Log4j2 vulnerable to Improper Input Validation and Uncontrolled Recursion

## Summary
Severity: High
Advisory: GHSA-p6xc-xr62-6r2g
CVE: CVE-2021-45105
CWE: CWE-20, CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-18
Source: https://github.com/advisories/GHSA-p6xc-xr62-6r2g
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.4.0 <2.12.3
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=2.13.0 <2.17.0
- Maven: `org.apache.logging.log4j:log4j-core` — affected >=0 <2.3.1
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.8.0 <1.9.2
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.10.0 <1.10.9
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=1.11.0 <1.11.12
- Maven: `org.ops4j.pax.logging:pax-logging-log4j2` — affected >=2.0.0 <2.0.13

## Details
Apache Log4j2 versions 2.0-alpha1 through 2.16.0 (excluding 2.12.3) did not protect from uncontrolled recursion from self-referential lookups. This allows an attacker with control over Thread Context Map data to cause a denial of service when a crafted string is interpreted. This issue was fixed in Log4j 2.17.0 and 2.12.3.


# Affected packages
Only the `org.apache.logging.log4j:log4j-core` package is directly affected by this vulnerability. The `org.apache.logging.log4j:log4j-api` should be kept at the same version as the `org.apache.logging.log4j:log4j-core` package to ensure compatability if in use.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45105
- https://www.zerodayinitiative.com/advisories/ZDI-21-1541
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.kb.cert.org/vuls/id/930724
- https://www.debian.org/security/2021/dsa-5024
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-log4j-qRuKNEbd
- https://security.netapp.com/advisory/ntap-20211218-0001
- https://sec.cloudapps.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-apache-log4j-qRuKNEbd
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2021-0032
- https://logging.apache.org/log4j/2.x/security.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SIG7FZULMNK2XF6FZRU4VWYDQXNMUGAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EOKPQGV24RRBBI4TBZUDQMM4MEH7MXCY
- https://lists.debian.org/debian-lts-announce/2021/12/msg00017.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-501673.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-479842.pdf
- http://www.openwall.com/lists/oss-security/2021/12/19/1
