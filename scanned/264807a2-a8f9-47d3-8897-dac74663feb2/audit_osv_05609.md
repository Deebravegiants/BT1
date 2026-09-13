# [H] Memory exhaustion when compiling regular expressions in regexp/syntax

## Summary
Severity: High
Advisory: BIT-golang-2022-41715
Aliases: CVE-2022-41715, GO-2022-1039
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-41715
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.19.0 <1.19.2

## Details
Programs which compile regular expressions from untrusted sources may be vulnerable to memory exhaustion or denial of service. The parsed regexp representation is linear in the size of the input, but in some cases the constant factor can be as high as 40,000, making relatively small regexps consume much larger amounts of memory. After fix, each regexp being parsed is limited to a 256 MB memory footprint. Regular expressions whose representation would use more space than that are rejected. Normal use of regular expressions is unaffected.

## References
- https://go.dev/cl/439356
- https://go.dev/issue/55949
- https://groups.google.com/g/golang-announce/c/xtuG5faxtaU
- https://pkg.go.dev/vuln/GO-2022-1039
- https://security.gentoo.org/glsa/202311-09
- https://nvd.nist.gov/vuln/detail/CVE-2022-41715
