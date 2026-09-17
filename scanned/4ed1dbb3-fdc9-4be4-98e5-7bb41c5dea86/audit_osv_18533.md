# [H] CVE-2020-28367

## Summary
Severity: High
Advisory: CVE-2020-28367
Aliases: BIT-golang-2020-28367, GO-2022-0476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-11-18
Source: https://osv.dev/vulnerability/CVE-2020-28367
Type: osv

## Details
Code injection in the go command with cgo before Go 1.14.12 and Go 1.15.5 allows arbitrary code execution at build time via malicious gcc flags specified via a #cgo directive.

## References
- https://go.dev/cl/267277
- https://go.dev/issue/42556
- https://go.googlesource.com/go/+/da7aa86917811a571e6634b45a457f918b8e6561
- https://groups.google.com/g/golang-announce/c/NpBGTTmKzpM
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://pkg.go.dev/vuln/GO-2022-0476
