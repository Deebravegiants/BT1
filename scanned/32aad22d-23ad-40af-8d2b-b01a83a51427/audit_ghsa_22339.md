# [M] Apache MyFaces Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-92cv-wv2c-8899
CVE: CVE-2010-2086
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-92cv-wv2c-8899
Type: github-advisory

## Affected
- Maven: `org.apache.myfaces.core:myfaces-core-module` — affected >=0
- Maven: `org.apache.myfaces.core:myfaces-core-module` — affected >=1.2.0

## Details
Apache MyFaces 1.1.7 and 1.2.8 (All previous versions are likely vulnerable), as used in IBM WebSphere Application Server and other applications, does not properly handle an unencrypted view state, which allows remote attackers to conduct cross-site scripting (XSS) attacks or execute arbitrary Expression Language (EL) statements via vectors that involve modifying the serialized view object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2086
- https://github.com/apache/myfaces
- https://www.trustwave.com/spiderlabs/advisories/TWSL2010-001.txt
- http://www.blackhat.com/presentations/bh-dc-10/Byrne_David/BlackHat-DC-2010-Byrne-SGUI-slides.pdf
