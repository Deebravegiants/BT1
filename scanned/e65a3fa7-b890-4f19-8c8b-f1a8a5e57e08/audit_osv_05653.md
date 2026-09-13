# [H] BIT-golang-2025-22867

## Summary
Severity: High
Advisory: BIT-golang-2025-22867
Aliases: CVE-2025-22867, GO-2025-3428
Ecosystem: Bitnami
Published: 2025-02-08
Source: https://osv.dev/vulnerability/BIT-golang-2025-22867
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-rc.2 <1.24.0-rc.3

## Details
On Darwin, building a Go module which contains CGO can trigger arbitrary code execution when using the Apple version of ld, due to usage of the @executable_path, @loader_path, or @rpath special values in a "#cgo LDFLAGS" directive. This issue only affected go1.24rc2.

## References
- https://go.dev/cl/646996
- https://go.dev/issue/71476
- https://groups.google.com/g/golang-dev/c/TYzikTgHK6Y
- https://pkg.go.dev/vuln/GO-2025-3428
