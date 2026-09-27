# [M] Invoking "go bug" follows symlinks in predictable temporary filenames in cmd/go

## Summary
Severity: Medium
Advisory: BIT-golang-2026-39819
Aliases: CVE-2026-39819, GO-2026-4978
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-golang-2026-39819
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.3

## Details
The "go bug" command writes to two files with predictable names in the system temporary directory (for example, "/tmp"). An attacker with access to the temporary directory can create a symlink in one of these names, causing "go bug" to overwrite the target of the symlink.

## References
- https://go.dev/cl/763882
- https://go.dev/issue/78584
- https://groups.google.com/g/golang-announce/c/qcCIEXso47M
- https://nvd.nist.gov/vuln/detail/CVE-2026-39819
- https://pkg.go.dev/vuln/GO-2026-4978
