# [M] Golang TIFF decoder vulnerable to excessive CPU consumption

## Summary
Severity: Medium
Advisory: GHSA-j3p8-6mrq-6g7h
CVE: CVE-2023-29407
CWE: CWE-834
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-02
Source: https://github.com/advisories/GHSA-j3p8-6mrq-6g7h
Type: github-advisory

## Affected
- Go: `golang.org/x/image` — affected >=0 <0.10.0

## Details
A maliciously-crafted image can cause excessive CPU consumption in decoding. A tiled image with a height of 0 and a very large width can cause excessive CPU consumption, despite the image size (width * height) appearing to be zero.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29407
- https://go.dev/cl/514897
- https://go.dev/issue/61581
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KO54NBDUJXKAZNGCFOEYL2LKK2RQP6K6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWH6Q7NVM4MV3GWFEU4PA67AWZHVFJQ2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XZTEP6JYILRBNDTNWTEQ5D4QUUVQBESK
- https://pkg.go.dev/vuln/GO-2023-1990
- https://security.netapp.com/advisory/ntap-20230831-0009
