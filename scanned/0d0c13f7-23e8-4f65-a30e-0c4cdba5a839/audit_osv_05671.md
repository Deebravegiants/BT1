# [M] Excessive CPU consumption when building archive index in archive/zip

## Summary
Severity: Medium
Advisory: BIT-golang-2025-61728
Aliases: CVE-2025-61728, GO-2026-4342
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-golang-2025-61728
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.6

## Details
archive/zip uses a super-linear file name indexing algorithm that is invoked the first time a file in an archive is opened. This can lead to a denial of service when consuming a maliciously constructed ZIP archive.

## References
- http://www.openwall.com/lists/oss-security/2026/01/15/4
- https://go.dev/cl/736713
- https://go.dev/issue/77102
- https://groups.google.com/g/golang-announce/c/Vd2tYVM8eUc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61728
- https://pkg.go.dev/vuln/GO-2026-4342
