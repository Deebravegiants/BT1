# [M] TOCTOU permits root escape on Linux via Root.Chmod in os in internal/syscall/unix

## Summary
Severity: Medium
Advisory: BIT-golang-2026-32282
Aliases: CVE-2026-32282, GO-2026-4864
Ecosystem: Bitnami
Published: 2026-04-13
Source: https://osv.dev/vulnerability/BIT-golang-2026-32282
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.26.0-0 <1.26.2

## Details
On Linux, if the target of Root.Chmod is replaced with a symlink while the chmod operation is in progress, Chmod can operate on the target of the symlink, even when the target lies outside the root. The Linux fchmodat syscall silently ignores the AT_SYMLINK_NOFOLLOW flag, which Root.Chmod uses to avoid symlink traversal. Root.Chmod checks its target before acting and returns an error if the target is a symlink lying outside the root, so the impact is limited to cases where the target is replaced with a symlink between the check and operation.

## References
- https://go.dev/cl/763761
- https://go.dev/issue/78293
- https://groups.google.com/g/golang-announce/c/0uYbvbPZRWU
- https://nvd.nist.gov/vuln/detail/CVE-2026-32282
- https://pkg.go.dev/vuln/GO-2026-4864
