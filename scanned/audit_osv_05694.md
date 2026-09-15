# [H] Root escape via symlink plus trailing slash in os

## Summary
Severity: High
Advisory: BIT-golang-2026-39822
Aliases: CVE-2026-39822, GO-2026-4970
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-golang-2026-39822
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
On Unix systems, opening a file in an os.Root improperly follows symlinks to locations outside of the Root when the final path component of the a path is a symbolic link and the path ends in /. For example, 'root.Open("symlink/")' will open "symlink" even when "symlink" is a symbolic link pointing outside of the root.

## References
- https://go.dev/cl/797880
- https://go.dev/issue/79005
- https://groups.google.com/g/golang-announce/c/OrmQE_Yp5Sc
- https://nvd.nist.gov/vuln/detail/CVE-2026-39822
- https://pkg.go.dev/vuln/GO-2026-4970
