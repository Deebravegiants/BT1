# [H] x/crypto/ssh vulnerable to panic via malformed packets

## Summary
Severity: High
Advisory: GHSA-gwc9-m7rh-j2ww
CVE: CVE-2021-43565
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-07
Source: https://github.com/advisories/GHSA-gwc9-m7rh-j2ww
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20211202192323-5770296d904e

## Details
The x/crypto/ssh package before 0.0.0-20211202192323-5770296d904e of golang.org/x/crypto allows an unauthenticated attacker to panic an SSH server. When using AES-GCM or ChaCha20Poly1305, consuming a malformed packet which contains an empty plaintext causes a panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43565
- https://go.dev/cl/368814
- https://go.dev/issues/49932
- https://groups.google.com/forum/#!forum/golang-announce
- https://groups.google.com/g/golang-announce/c/2AR1sKiM-Qs
- https://pkg.go.dev/vuln/GO-2022-0968
