# [H] BIT-golang-2024-45340

## Summary
Severity: High
Advisory: BIT-golang-2024-45340
Aliases: CVE-2024-45340, GO-2025-3383
Ecosystem: Bitnami
Published: 2025-01-30
Source: https://osv.dev/vulnerability/BIT-golang-2024-45340
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.0-rc.2

## Details
Credentials provided via the new GOAUTH feature were not being properly segmented by domain, allowing a malicious server to request credentials they should not have access to. By default, unless otherwise set, this only affected credentials stored in the users .netrc file.

## References
- https://go.dev/cl/643097
- https://go.dev/issue/71249
- https://groups.google.com/g/golang-dev/c/CAWXhan3Jww/m/bk9LAa-lCgAJ
- https://pkg.go.dev/vuln/GO-2025-3383
