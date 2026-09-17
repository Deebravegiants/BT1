# [C] Arbitrary code execution via go.mod toolchain directive in cmd/go

## Summary
Severity: Critical
Advisory: BIT-golang-2023-39320
Aliases: CVE-2023-39320, GO-2023-2042
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-39320
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.21.0 <1.21.1

## Details
The go.mod toolchain directive, introduced in Go 1.21, can be leveraged to execute scripts and binaries relative to the root of the module when the "go" command was executed within the module. This applies to modules downloaded using the "go" command from the module proxy, as well as modules downloaded directly using VCS software.

## References
- https://go.dev/cl/526158
- https://go.dev/issue/62198
- https://groups.google.com/g/golang-dev/c/2C5vbR-UNkI/m/L1hdrPhfBAAJ
- https://pkg.go.dev/vuln/GO-2023-2042
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20231020-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39320
