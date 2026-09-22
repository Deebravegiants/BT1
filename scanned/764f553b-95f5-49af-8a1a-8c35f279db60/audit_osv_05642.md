# [M] Errors returned from JSON marshaling may break template escaping in html/template

## Summary
Severity: Medium
Advisory: BIT-golang-2024-24785
Aliases: CVE-2024-24785, GO-2024-2610
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-golang-2024-24785
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.1

## Details
If errors returned from MarshalJSON methods contain user controlled data, they may be used to break the contextual auto-escaping behavior of the html/template package, allowing for subsequent actions to inject unexpected content into templates.

## References
- https://go.dev/cl/564196
- https://go.dev/issue/65697
- https://groups.google.com/g/golang-announce/c/5pwGVUPoMbg
- https://pkg.go.dev/vuln/GO-2024-2610
- https://security.netapp.com/advisory/ntap-20240329-0008/
- http://www.openwall.com/lists/oss-security/2024/03/08/4
- https://nvd.nist.gov/vuln/detail/CVE-2024-24785
