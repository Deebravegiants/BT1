# [H] Improper Verification of Cryptographic Signature in golang.org/x/crypto

## Summary
Severity: High
Advisory: GHSA-ffhg-7mh4-33c4
CVE: CVE-2020-9283
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-ffhg-7mh4-33c4
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20200220183623-bac4c82f6975

## Details
golang.org/x/crypto before v0.0.0-20200220183623-bac4c82f6975 for Go allows a panic during signature verification in the golang.org/x/crypto/ssh package. A client can attack an SSH server that accepts public keys. Also, a server can attack any SSH client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9283
- https://github.com/golang/crypto/commit/bac4c82f69751a6dd76e702d54b3ceb88adab236
- https://github.com/golang/crypto
- https://go.dev/cl/220357
- https://go.googlesource.com/crypto/+/bac4c82f69751a6dd76e702d54b3ceb88adab236
- https://groups.google.com/forum/#!topic/golang-announce/3L45YRc91SY
- https://groups.google.com/g/golang-announce/c/3L45YRc91SY
- https://lists.debian.org/debian-lts-announce/2020/10/msg00014.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00027.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00031.html
- https://pkg.go.dev/vuln/GO-2020-0012
- https://www.exploit-db.com/exploits/48121
- http://packetstormsecurity.com/files/156480/Go-SSH-0.0.2-Denial-Of-Service.html
