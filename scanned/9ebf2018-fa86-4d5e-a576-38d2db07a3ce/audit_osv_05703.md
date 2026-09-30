# [M] Avoid quadratic complexity in resolvePath in net/url

## Summary
Severity: Medium
Advisory: BIT-golang-2026-56860
Aliases: CVE-2026-56860, GO-2026-6218
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-golang-2026-56860
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
Previously, resolving relative paths containing parent directory ('..') segments performed string conversions and buffer rewrites on each step, resulting in quadratic time complexity and high memory allocation overhead. Now, path resolution operates on a byte buffer using index-based backtracking for '..' segments, eliminating the quadratic time complexity and significantly reducing memory allocations.

## References
- https://go.dev/cl/803681
- https://go.dev/issue/80494
- https://groups.google.com/g/golang-announce/c/94pEornpRlI
- https://nvd.nist.gov/vuln/detail/CVE-2026-56860
- https://pkg.go.dev/vuln/GO-2026-6218
