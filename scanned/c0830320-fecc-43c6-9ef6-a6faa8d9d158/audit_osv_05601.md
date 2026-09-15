# [H] Stack exhaustion when reading certain archives in compress/gzip

## Summary
Severity: High
Advisory: BIT-golang-2022-30631
Aliases: CVE-2022-30631, GO-2022-0524
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-30631
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.18.0 <1.18.4

## Details
Uncontrolled recursion in Reader.Read in compress/gzip before Go 1.17.12 and Go 1.18.4 allows an attacker to cause a panic due to stack exhaustion via an archive containing a large number of concatenated 0-length compressed files.

## References
- https://go.dev/cl/417067
- https://go.dev/issue/53168
- https://go.googlesource.com/go/+/b2b8872c876201eac2d0707276c6999ff3eb185e
- https://groups.google.com/g/golang-announce/c/nqrv9fbR0zE
- https://pkg.go.dev/vuln/GO-2022-0524
- https://nvd.nist.gov/vuln/detail/CVE-2022-30631
