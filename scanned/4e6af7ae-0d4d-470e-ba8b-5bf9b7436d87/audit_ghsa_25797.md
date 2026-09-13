# [H] Deeply nested json in jackson-databind

## Summary
Severity: High
Advisory: GHSA-57j2-w4cx-62h2
CVE: CVE-2020-36518
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-57j2-w4cx-62h2
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.13.0 <2.13.2.1
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=0 <2.12.6.1

## Details
jackson-databind is a data-binding package for the Jackson Data Processor. jackson-databind allows a Java stack overflow exception and denial of service via a large depth of nested objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36518
- https://github.com/FasterXML/jackson-databind/issues/2816
- https://github.com/FasterXML/jackson-databind/commit/0a8157c6ca478b1bc7be4ba7dccdb3863275f0de
- https://github.com/FasterXML/jackson-databind/commit/3cc52f82ecf943e06c1d7c3b078e405fb3923d2b
- https://github.com/FasterXML/jackson-databind/commit/8238ab41d0350fb915797c89d46777b4496b74fd
- https://github.com/FasterXML/jackson-databind/commit/b3587924ee5d8695942f364d0d404d48d0ea6126
- https://github.com/FasterXML/jackson-databind/commit/fcfc4998ec23f0b1f7f8a9521c2b317b6c25892b
- https://github.com/FasterXML/jackson-databind
- https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.12
- https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.13
- https://lists.debian.org/debian-lts-announce/2022/05/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00035.html
- https://security.netapp.com/advisory/ntap-20220506-0004
- https://www.debian.org/security/2022/dsa-5283
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
