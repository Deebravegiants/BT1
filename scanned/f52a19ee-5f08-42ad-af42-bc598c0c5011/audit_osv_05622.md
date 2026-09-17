# [C] Code injection via go command with cgo in cmd/go

## Summary
Severity: Critical
Advisory: BIT-golang-2023-29402
Aliases: CVE-2023-29402, GO-2023-1839
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-29402
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.5

## Details
The go command may generate unexpected code at build time when using cgo. This may result in unexpected behavior when running a go program which uses cgo. This may occur when running an untrusted module which contains directories with newline characters in their names. Modules which are retrieved using the go command, i.e. via "go get", are not affected (modules retrieved using GOPATH-mode, i.e. GO111MODULE=off, may be affected).

## References
- https://go.dev/cl/501226
- https://go.dev/issue/60167
- https://groups.google.com/g/golang-announce/c/q5135a9d924/m/j0ZoAJOHAwAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NZ2O6YCO2IZMZJELQGZYR2WAUNEDLYV6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XBS3IIK6ADV24C5ULQU55QLT2UE762ZX/
- https://pkg.go.dev/vuln/GO-2023-1839
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20241213-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29402
