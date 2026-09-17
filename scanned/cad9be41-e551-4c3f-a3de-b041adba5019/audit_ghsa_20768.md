# [M] Denial of Service due to parser crash

## Summary
Severity: Medium
Advisory: GHSA-3f7h-mf4q-vrm4
CVE: CVE-2022-40152
CWE: CWE-121, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-17
Source: https://github.com/advisories/GHSA-3f7h-mf4q-vrm4
Type: github-advisory

## Affected
- Maven: `com.fasterxml.woodstox:woodstox-core` — affected >=6.0.0 <6.4.0
- Maven: `com.fasterxml.woodstox:woodstox-core` — affected >=0 <5.4.0

## Details
Those using FasterXML/woodstox to seralize XML data may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow. This effect may support a denial of service attack.

This vulnerability is only relevant for users making use of the DTD parsing functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40152
- https://github.com/FasterXML/woodstox/issues/157
- https://github.com/FasterXML/woodstox/issues/160
- https://github.com/x-stream/xstream/issues/304
- https://github.com/FasterXML/woodstox/pull/159
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=47434
- https://github.com/FasterXML/woodstox
