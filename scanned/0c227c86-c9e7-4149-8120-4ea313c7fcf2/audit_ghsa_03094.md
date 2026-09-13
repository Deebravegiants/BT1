# [C] Improper Authentication in Apache Shiro

## Summary
Severity: Critical
Advisory: GHSA-26gr-cvq3-qxgf
CVE: CVE-2020-1957
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-26gr-cvq3-qxgf
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <1.5.2

## Details
Apache Shiro before 1.5.2, when using Apache Shiro with Spring dynamic controllers, a specially crafted request may cause an authentication bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1957
- https://github.com/apache/shiro
- https://lists.apache.org/thread.html/r17f371fc89d34df2d0c8131473fbc68154290e1be238895648f5a1e6%40%3Cdev.shiro.apache.org%3E
- https://lists.apache.org/thread.html/r2d2612c034ab21a3a19d2132d47d3e4aa70105008dd58af62b653040@%3Ccommits.shiro.apache.org%3E
- https://lists.apache.org/thread.html/rab1972d6b177f7b5c3dde9cfb0a40f03bca75f0eaf1d8311e5762cb3@%3Ccommits.shiro.apache.org%3E
- https://lists.apache.org/thread.html/rb3982edf8bc8fcaa7a308e25a12d294fb4aac1f1e9d4e14fda639e77@%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/rc64fb2336683feff3580c3c3a8b28e80525077621089641f2f386b63@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/rc8b39ea8b3ef71ddc1cd74ffc866546182683c8adecf19c263fe7ac0@%3Ccommits.shiro.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/04/msg00014.html
