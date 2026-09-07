# [M] Cross site scripting in datatables.net 

## Summary
Severity: Medium
Advisory: GHSA-h73q-5wmj-q8pj
CVE: CVE-2021-23445
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-29
Source: https://github.com/advisories/GHSA-h73q-5wmj-q8pj
Type: github-advisory

## Affected
- npm: `datatables.net` — affected >=0 <1.11.3

## Details
This affects the package datatables.net before 1.11.3. If an array is passed to the HTML escape entities function it would not have its contents escaped.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23445
- https://github.com/DataTables/Dist-DataTables/commit/59a8d3f8a3c1138ab08704e783bc52bfe88d7c9b
- https://cdn.datatables.net/1.11.3
- https://github.com/DataTables/Dist-DataTables
- https://lists.debian.org/debian-lts-announce/2023/08/msg00018.html
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1715371
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1715376
- https://snyk.io/vuln/SNYK-JS-DATATABLESNET-1540544
