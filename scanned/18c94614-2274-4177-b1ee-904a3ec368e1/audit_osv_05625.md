# [C] Improper sanitization of LDFLAGS with embedded spaces in go command with cgo in cmd/go

## Summary
Severity: Critical
Advisory: BIT-golang-2023-29405
Aliases: CVE-2023-29405, GO-2023-1842
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-29405
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.5

## Details
The go command may execute arbitrary code at build time when using cgo. This may occur when running "go get" on a malicious module, or when running any other command which builds untrusted code. This is can by triggered by linker flags, specified via a "#cgo LDFLAGS" directive. Flags containing embedded spaces are mishandled, allowing disallowed flags to be smuggled through the LDFLAGS sanitization by including them in the argument of another flag. This only affects usage of the gccgo compiler.

## References
- https://go.dev/cl/501224
- https://go.dev/issue/60306
- https://groups.google.com/g/golang-announce/c/q5135a9d924/m/j0ZoAJOHAwAJ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NZ2O6YCO2IZMZJELQGZYR2WAUNEDLYV6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XBS3IIK6ADV24C5ULQU55QLT2UE762ZX/
- https://pkg.go.dev/vuln/GO-2023-1842
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20241206-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29405
