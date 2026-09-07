# [M] Jenkins Delivery Pipeline Plugin Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g364-c7w5-93wh
CVE: CVE-2017-1000404
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g364-c7w5-93wh
Type: github-advisory

## Affected
- Maven: `se.diabol.jenkins.pipeline:delivery-pipeline-plugin` — affected >=0 <1.0.8

## Details
The Jenkins Delivery Pipeline Plugin version 1.0.7 and earlier used the unescaped content of the query parameter 'fullscreen' in its JavaScript, resulting in a cross-site scripting vulnerability through specially crafted URLs. Version 1.0.8 of the plugin converts the value to a boolean (true/false) and inserts that into the page instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000404
- https://jenkins.io/security/advisory/2017-11-16
- http://www.securityfocus.com/bid/101927
