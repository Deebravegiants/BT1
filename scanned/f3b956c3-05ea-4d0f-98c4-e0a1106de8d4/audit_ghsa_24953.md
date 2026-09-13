# [M] Apache POI's XLSX2CSV Example XML External Entity (XXE) Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pmqq-7wfv-jfff
CVE: CVE-2016-5000
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pmqq-7wfv-jfff
Type: github-advisory

## Affected
- Maven: `org.apache.poi:poi-examples` — affected >=0 <3.14

## Details
The XLSX2CSV example in Apache POI before 3.14 allows remote attackers to read arbitrary files via a crafted OpenXML document containing an external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5000
- https://lists.apache.org/list.html?user@poi.apache.org
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://www-01.ibm.com/support/docview.wss?uid=swg21996759
