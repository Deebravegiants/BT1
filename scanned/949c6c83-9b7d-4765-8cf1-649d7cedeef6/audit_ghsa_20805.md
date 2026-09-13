# [C] Apache Calcite before 1.32.0 vulnerable to potential XML External Entity (XXE) attack

## Summary
Severity: Critical
Advisory: GHSA-fj2m-w3wv-x9pr
CVE: CVE-2022-39135
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-12
Source: https://github.com/advisories/GHSA-fj2m-w3wv-x9pr
Type: github-advisory

## Affected
- Maven: `org.apache.calcite:calcite-core` — affected >=0 <1.32.0

## Details
In Apache Calcite prior to version 1.32.0 the SQL operators EXISTS_NODE, EXTRACT_XML, XML_TRANSFORM and EXTRACT_VALUE do not restrict XML External Entity references in their configuration, which makes them vulnerable to a potential XML External Entity (XXE) attack. Therefore any client exposing these operators, typically by using Oracle dialect (the first three) or MySQL dialect (the last one), is affected by this vulnerability (the extent of it will depend on the user under which the application is running). From Apache Calcite 1.32.0 onwards, Document Type Declarations and XML External Entity resolution are disabled on the impacted operators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-39135
- https://lists.apache.org/thread/ohdnhlgm6jvt3srw8l7spkm2d5vwm082
- http://www.openwall.com/lists/oss-security/2022/11/21/3
