# [M] Unexpected paths returned from LookPath in os/exec

## Summary
Severity: Medium
Advisory: BIT-golang-2025-47906
Aliases: CVE-2025-47906, GO-2025-3956
Ecosystem: Bitnami
Published: 2025-09-20
Source: https://osv.dev/vulnerability/BIT-golang-2025-47906
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0 <1.24.6

## Details
If the PATH environment variable contains paths which are executables (rather than just directories), passing certain strings to LookPath ("", ".", and ".."), can result in the binaries listed in the PATH being unexpectedly returned.

## References
- https://go.dev/cl/691775
- https://go.dev/issue/74466
- https://groups.google.com/g/golang-announce/c/x5MKroML2yM
- https://nvd.nist.gov/vuln/detail/CVE-2025-47906
- https://pkg.go.dev/vuln/GO-2025-3956
- http://www.openwall.com/lists/oss-security/2025/08/06/1
