# [M] UberFire Framework Improperly Restricts Paths

## Summary
Severity: Medium
Advisory: GHSA-6h58-c7r7-g2hw
CVE: CVE-2014-8114
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-6h58-c7r7-g2hw
Type: github-advisory

## Affected
- Maven: `org.uberfire:uberfire-parent` — affected >=0.3.0.Beta5

## Details
The UberFire Framework 0.3.x does not properly restrict paths, which allows remote attackers to (1) execute arbitrary code by uploading crafted content to FileUploadServlet or (2) read arbitrary files via vectors involving FileDownloadServlet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8114
- https://github.com/uberfire/uberfire/commit/21ec50eb15
- https://web.archive.org/web/20200227080813/http://www.securityfocus.com/bid/88199
- http://rhn.redhat.com/errata/RHSA-2015-0234.html
- http://rhn.redhat.com/errata/RHSA-2015-0235.html
