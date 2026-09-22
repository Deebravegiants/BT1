# [H] Comments in display names are incorrectly handled in net/mail

## Summary
Severity: High
Advisory: BIT-golang-2024-24784
Aliases: CVE-2024-24784, GO-2024-2609
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-golang-2024-24784
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.1

## Details
The ParseAddressList function incorrectly handles comments (text within parentheses) within display names. Since this is a misalignment with conforming address parsers, it can result in different trust decisions being made by programs using different parsers.

## References
- https://go.dev/cl/555596
- https://go.dev/issue/65083
- https://groups.google.com/g/golang-announce/c/5pwGVUPoMbg
- https://pkg.go.dev/vuln/GO-2024-2609
- https://security.netapp.com/advisory/ntap-20240329-0007/
- http://www.openwall.com/lists/oss-security/2024/03/08/4
- https://nvd.nist.gov/vuln/detail/CVE-2024-24784
