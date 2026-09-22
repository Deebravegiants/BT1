# [H] Arbitrary code execution during build via line directives in cmd/go

## Summary
Severity: High
Advisory: BIT-golang-2023-39323
Aliases: CVE-2023-39323, GO-2023-2095
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-39323
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.21.0 <1.21.2

## Details
Line directives ("//line") can be used to bypass the restrictions on "//go:cgo_" directives, allowing blocked linker and compiler flags to be passed during compilation. This can result in unexpected execution of arbitrary code when running "go build". The line directive requires the absolute path of the file in which the directive lives, which makes exploiting this issue significantly more complex.

## References
- https://go.dev/cl/533215
- https://go.dev/issue/63211
- https://groups.google.com/g/golang-announce/c/XBa1oHDevAo
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CLB4TW7KALB3EEQWNWCN7OUIWWVWWCG2/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KSEGD2IWKNUO3DWY4KQGUQM5BISRWHQE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XFOIBB4YFICHDM7IBOP7PWXW3FX4HLL2/
- https://pkg.go.dev/vuln/GO-2023-2095
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20231020-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39323
