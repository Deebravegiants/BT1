# [H] Stack exhaustion on crafted paths in path/filepath

## Summary
Severity: High
Advisory: BIT-golang-2022-30632
Aliases: CVE-2022-30632, GO-2022-0522
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30632
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in Glob in path/filepath before Go 1.17.12 and Go 1.18.4 allows an attacker to cause a panic due to stack exhaustion via a path containing a large number of path separators.

## References
- https://go.dev/cl/417066
- https://go.dev/issue/53416
- https://go.googlesource.com/go/+/ac68c6c683409f98250d34ad282b9e1b0c9095ef
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0522
- https://nvd.nist.gov/vuln/detail/CVE-2022-30632
