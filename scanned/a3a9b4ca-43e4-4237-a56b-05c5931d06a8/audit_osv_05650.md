# [M] Inconsistent handling of O_CREATE|O_EXCL on Unix and Windows in os in syscall

## Summary
Severity: Medium
Advisory: BIT-golang-2025-0913
Aliases: CVE-2025-0913, GO-2025-3750
Ecosystem: Bitnami
Published: 2025-06-14
Source: https://osv.dev/vulnerability/BIT-golang-2025-0913
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.4

## Details
os.OpenFile(path, os.O_CREATE|O_EXCL) behaved differently on Unix and Windows systems when the target path was a dangling symlink. On Unix systems, OpenFile with O_CREATE and O_EXCL flags never follows symlinks. On Windows, when the target path was a symlink to a nonexistent location, OpenFile would create a file in that location. OpenFile now always returns an error when the O_CREATE and O_EXCL flags are both set and the target path is a symlink.

## References
- https://go.dev/cl/672396
- https://go.dev/issue/73702
- https://groups.google.com/g/golang-announce/c/ufZ8WpEsA3A
- https://nvd.nist.gov/vuln/detail/CVE-2025-0913
- https://pkg.go.dev/vuln/GO-2025-3750
