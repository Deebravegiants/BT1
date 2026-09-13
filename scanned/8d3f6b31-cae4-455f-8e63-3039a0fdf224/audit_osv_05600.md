# [H] Stack exhaustion in Glob on certain paths in io/fs

## Summary
Severity: High
Advisory: BIT-golang-2022-30630
Aliases: CVE-2022-30630, GO-2022-0527
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30630
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in Glob in io/fs before Go 1.17.12 and Go 1.18.4 allows an attacker to cause a panic due to stack exhaustion via a path which contains a large number of path separators.

## References
- https://go.dev/cl/417065
- https://go.dev/issue/53415
- https://go.googlesource.com/go/+/fa2d41d0ca736f3ad6b200b2a4e134364e9acc59
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0527
- https://nvd.nist.gov/vuln/detail/CVE-2022-30630
