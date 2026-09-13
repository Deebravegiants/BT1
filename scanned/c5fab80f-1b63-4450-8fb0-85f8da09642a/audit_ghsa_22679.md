# [M] Apache Axis allows Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-2c4w-2px5-9x3x
CVE: CVE-2007-2353
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-2c4w-2px5-9x3x
Type: github-advisory

## Affected
- Maven: `org.apache.axis:axis` — affected >=0 <1.2

## Details
Apache Axis 1.0 allows remote attackers to obtain sensitive information by requesting a non-existent WSDL file, which reveals the installation path in the resulting exception message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-2353
- https://github.com/albfernandez/axis1-java/issues/34#issuecomment-1006693110
- https://github.com/albfernandez/axis1-java/commit/32f35038ecae2c7a7f2e904b2289fd383f6f4d1f
- https://github.com/apache/axis-axis1-java/commit/2fdbb91c5e861e804db70cada188b1d7c1603513
- https://github.com/apache/axis-axis1-java/commit/7ba89deb2eb21615630f18e96a35bfdec7f7cfed
- https://exchange.xforce.ibmcloud.com/vulnerabilities/34167
- https://github.com/apache/axis-axis1-java
- http://attrition.org/pipermail/vim/2007-April/001562.html
