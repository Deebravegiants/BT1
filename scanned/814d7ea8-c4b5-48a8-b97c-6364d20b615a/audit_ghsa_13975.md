# [M] Uncontrolled Resource Consumption in golang.org/x/image

## Summary
Severity: Medium
Advisory: GHSA-qgc7-mgm3-q253
CVE: CVE-2022-41727
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-17
Source: https://github.com/advisories/GHSA-qgc7-mgm3-q253
Type: github-advisory

## Affected
- Go: `golang.org/x/image` — affected >=0 <0.5.0

## Details
An attacker can craft a malformed TIFF image which will consume a significant amount of memory when passed to DecodeConfig. This could lead to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41727
- https://go.dev/cl/468195
- https://go.dev/issue/58003
- https://groups.google.com/g/golang-announce/c/ag-FiyjlD5o
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KO54NBDUJXKAZNGCFOEYL2LKK2RQP6K6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWH6Q7NVM4MV3GWFEU4PA67AWZHVFJQ2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XZTEP6JYILRBNDTNWTEQ5D4QUUVQBESK
- https://pkg.go.dev/vuln/GO-2023-1572
