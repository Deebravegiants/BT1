# [M] Golang TIFF decoder does not place a limit on the size of compressed tile data

## Summary
Severity: Medium
Advisory: GHSA-x92r-3vfx-4cv3
CVE: CVE-2023-29408
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-02
Source: https://github.com/advisories/GHSA-x92r-3vfx-4cv3
Type: github-advisory

## Affected
- Go: `golang.org/x/image` — affected >=0 <0.10.0

## Details
The TIFF decoder does not place a limit on the size of compressed tile data. A maliciously-crafted image can exploit this to cause a small image (both in terms of pixel width/height, and encoded size) to make the decoder decode large amounts of compressed data, consuming excessive memory and CPU.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29408
- https://go.dev/cl/514897
- https://go.dev/issue/61582
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KO54NBDUJXKAZNGCFOEYL2LKK2RQP6K6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWH6Q7NVM4MV3GWFEU4PA67AWZHVFJQ2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XZTEP6JYILRBNDTNWTEQ5D4QUUVQBESK
- https://pkg.go.dev/vuln/GO-2023-1989
- https://security.netapp.com/advisory/ntap-20230831-0009
