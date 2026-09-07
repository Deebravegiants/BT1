# [M] MPXJ path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p9j6-4pjr-gp48
CVE: CVE-2020-35460
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-12-18
Source: https://github.com/advisories/GHSA-p9j6-4pjr-gp48
Type: github-advisory

## Affected
- Maven: `net.sf.mpxj:mpxj` — affected >=0 <8.3.5

## Details
common/InputStreamHelper.java in Packwood MPXJ before 8.3.5 allows directory traversal in the zip stream handler flow, leading to the writing of files to arbitrary locations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35460
- https://github.com/joniles/mpxj/commit/8eaf4225048ea5ba7e59ef4556dab2098fcc4a1d
- https://www.oracle.com/security-alerts/cpujan2021.html
- http://www.mpxj.org/changes-report.html#a8.3.5
