# [H] Improper handling of empty HTML attributes in html/template

## Summary
Severity: High
Advisory: BIT-golang-2023-29400
Aliases: CVE-2023-29400, GO-2023-1753
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-29400
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.4

## Details
Templates containing actions in unquoted HTML attributes (e.g. "attr={{.}}") executed with empty input can result in output with unexpected results when parsed due to HTML normalization rules. This may allow injection of arbitrary attributes into tags.

## References
- https://go.dev/cl/491617
- https://go.dev/issue/59722
- https://groups.google.com/g/golang-announce/c/MEb0UyuSMsU
- https://pkg.go.dev/vuln/GO-2023-1753
- https://security.netapp.com/advisory/ntap-20241213-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29400
