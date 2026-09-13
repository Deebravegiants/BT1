# [H] XML External Entity Reference in ureport

## Summary
Severity: High
Advisory: GHSA-fhj6-gr87-g4cj
CVE: CVE-2023-24187
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-14
Source: https://github.com/advisories/GHSA-fhj6-gr87-g4cj
Type: github-advisory

## Affected
- Maven: `com.bstek.ureport:ureport2-core` — affected >=0

## Details
An XML External Entity (XXE) vulnerability in ureport v2.2.9 allows attackers to execute arbitrary code via uploading a crafted XML file to /ureport/designer/saveReportFile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24187
- https://github.com/Venus-WQLab/bug_report/blob/main/ureport/ureport-cve-2023-24187.md
- https://github.com/cgddgc/vulns/blob/main/ureport2-vuln-des.md
- https://github.com/youseries/ureport
- http://ureport.com
