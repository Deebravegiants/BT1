# [M] Infinite loop in Apache MINA

## Summary
Severity: Medium
Advisory: GHSA-6mcm-j9cj-3vc3
CVE: CVE-2021-41973
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-6mcm-j9cj-3vc3
Type: github-advisory

## Affected
- Maven: `org.apache.mina:mina-core` — affected >=2.1.0 <2.1.5
- Maven: `org.apache.mina:mina-core` — affected >=0 <2.0.22

## Details
In Apache MINA, a specifically crafted, malformed HTTP request may cause the HTTP Header decoder to loop indefinitely. The decoder assumed that the HTTP Header begins at the beginning of the buffer and loops if there is more data than expected. Please update MINA to 2.1.5 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41973
- https://lists.apache.org/thread.html/r0b907da9340d5ff4e6c1a4798ef4e79700a668657f27cca8a39e9250%40%3Cdev.mina.apache.org%3E
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://www.openwall.com/lists/oss-security/2021/11/01/2
- http://www.openwall.com/lists/oss-security/2021/11/01/8
