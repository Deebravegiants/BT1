# [M] golang.org/x/crypto/salsa20/salsa uses insufficiently random values

## Summary
Severity: Medium
Advisory: GHSA-r5c5-pr8j-pfp7
CVE: CVE-2019-11840
CWE: CWE-330
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r5c5-pr8j-pfp7
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20190320223903-b7391e95e576

## Details
An issue was discovered in supplementary Go cryptography libraries, aka golang-googlecode-go-crypto, before 2019-03-20. A flaw was found in the amd64 implementation of golang.org/x/crypto/salsa20 and golang.org/x/crypto/salsa20/salsa. If more than 256 GiB of keystream is generated, or if the counter otherwise grows greater than 32 bits, the amd64 implementation will first generate incorrect output, and then cycle back to previously generated keystream. Repeated keystream bytes can lead to loss of confidentiality in encryption applications, or to predictability in CSPRNG applications.

### Specific Go Packages Affected
golang.org/x/crypto/salsa20/salsa

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11840
- https://github.com/golang/go/issues/30965
- https://bugzilla.redhat.com/show_bug.cgi?id=1691529
- https://github.com/golang/go
- https://go.dev/cl/168406
- https://go.dev/issue/30965
- https://go.googlesource.com/crypto/+/b7391e95e576cacdcdd422573063bc057239113d
- https://groups.google.com/forum/#!msg/golang-announce/tjyNcJxb2vQ/n0NRBziSCAAJ
- https://groups.google.com/g/golang-announce/c/tjyNcJxb2vQ/m/n0NRBziSCAAJ
- https://lists.debian.org/debian-lts-announce/2019/06/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00014.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00016.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00015.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00017.html
- https://pkg.go.dev/vuln/GO-2022-0209
