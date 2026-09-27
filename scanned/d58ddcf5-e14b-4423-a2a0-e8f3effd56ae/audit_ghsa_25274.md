# [M] Apache Tika vulnerable to uncontrolled memory consumption

## Summary
Severity: Medium
Advisory: GHSA-7qcq-xp2f-56f6
CVE: CVE-2022-25169
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7qcq-xp2f-56f6
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika` — affected >=0 <1.28.2
- Maven: `org.apache.tika:tika` — affected >=2.0.0 <2.4.0

## Details
The BPG parser in versions of Apache Tika before 1.28.2 and 2.4.0 may allocate an unreasonable amount of memory on carefully crafted files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25169
- https://github.com/apache/tika
- https://lists.apache.org/thread/t3tb51sf0k2pmbnzsrrrm23z9r1c10rk
- https://security.netapp.com/advisory/ntap-20220804-0004
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2022/05/16/4
