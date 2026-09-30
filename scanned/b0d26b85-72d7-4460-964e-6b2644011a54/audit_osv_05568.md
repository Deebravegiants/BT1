# [H] BIT-golang-2020-28851

## Summary
Severity: High
Advisory: BIT-golang-2020-28851
Aliases: CVE-2020-28851
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-28851
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.15.4 <1.15.5

## Details
In x/text in Go 1.15.4, an "index out of range" panic occurs in language.ParseAcceptLanguage while parsing the -u- extension. (x/text/language is supposed to be able to parse an HTTP Accept-Language header.)

## References
- https://github.com/golang/go/issues/42535
- https://security.netapp.com/advisory/ntap-20210212-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2020-28851
