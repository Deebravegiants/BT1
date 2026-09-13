# [M] Unbounded allocation when parsing GNU sparse map in archive/tar

## Summary
Severity: Medium
Advisory: BIT-golang-2025-58183
Aliases: CVE-2025-58183, GO-2025-4014
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-58183
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
tar.Reader does not set a maximum size on the number of sparse region data blocks in GNU tar pax 1.0 sparse files. A maliciously-crafted archive containing a large number of sparse regions can cause a Reader to read an unbounded amount of data from the archive into memory. When reading from a compressed source, a small compressed input can result in large allocations.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709861
- https://go.dev/issue/75677
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-58183
- https://pkg.go.dev/vuln/GO-2025-4014
