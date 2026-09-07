# [H] Uncontrolled Resource Consumption in FasterXML jackson-databind

## Summary
Severity: High
Advisory: GHSA-rgv9-q543-rqg4
CVE: CVE-2022-42004
CWE: CWE-400, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-03
Source: https://github.com/advisories/GHSA-rgv9-q543-rqg4
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.4.0-rc1 <2.12.7.1
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.13.0 <2.13.4

## Details
In FasterXML jackson-databind before 2.12.7.1 and in 2.13.x before 2.13.4, resource exhaustion can occur because of a lack of a check in BeanDeserializer._deserializeFromArray to prevent use of deeply nested arrays. This issue can only happen when the `UNWRAP_SINGLE_VALUE_ARRAYS` feature is explicitly enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42004
- https://github.com/FasterXML/jackson-databind/issues/3582
- https://github.com/FasterXML/jackson-databind/commit/063183589218fec19a9293ed2f17ec53ea80ba88
- https://github.com/FasterXML/jackson-databind/commit/0e37a39502439ecbaa1a5b5188387c01bf7f7fa1
- https://github.com/FasterXML/jackson-databind/commit/35de19e7144c4df8ab178b800ba86e80c3d84252
- https://github.com/FasterXML/jackson-databind/commit/cd090979b7ea78c75e4de8a4aed04f7e9fa8deea
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=50490
- https://github.com/FasterXML/jackson-databind
- https://lists.debian.org/debian-lts-announce/2022/11/msg00035.html
- https://security.gentoo.org/glsa/202210-21
- https://security.netapp.com/advisory/ntap-20221118-0008
- https://www.debian.org/security/2022/dsa-5283
