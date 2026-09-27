# [H] Arbitrary code execution in go command with cgo in cmd/go and cmd/cgo

## Summary
Severity: High
Advisory: BIT-golang-2020-28366
Aliases: CVE-2020-28366, GO-2022-0475
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2020-28366
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.15.0 <1.15.5

## Details
Code injection in the go command with cgo before Go 1.14.12 and Go 1.15.5 allows arbitrary code execution at build time via a malicious unquoted symbol name in a linked object file.

## References
- https://go.dev/cl/269658
- https://go.dev/issue/42559
- https://go.googlesource.com/go/+/062e0e5ce6df339dc26732438ad771f73dbf2292
- https://groups.google.com/g/golang-announce/c/NpBGTTmKzpM
- https://pkg.go.dev/vuln/GO-2022-0475
- https://nvd.nist.gov/vuln/detail/CVE-2020-28366
