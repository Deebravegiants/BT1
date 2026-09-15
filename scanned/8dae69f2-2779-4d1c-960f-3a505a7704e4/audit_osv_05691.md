# [M] Invoking "go tool pack" does not sanitize output paths in cmd/go

## Summary
Severity: Medium
Advisory: BIT-golang-2026-39817
Aliases: CVE-2026-39817, GO-2026-4979
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-golang-2026-39817
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.3

## Details
The "go tool pack" subcommand (usually used only by the compiler as an internal tool with known-good inputs) does not sanitize output filenames. Extracting a malicious archive file with the "pack" subcommand can write files to arbitrary locations on the filesystem.

## References
- https://go.dev/cl/767520
- https://go.dev/issue/78778
- https://groups.google.com/g/golang-announce/c/qcCIEXso47M
- https://nvd.nist.gov/vuln/detail/CVE-2026-39817
- https://pkg.go.dev/vuln/GO-2026-4979
