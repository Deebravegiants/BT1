# [H] Unbounded memory consumption when reading headers in archive/tar

## Summary
Severity: High
Advisory: BIT-golang-2022-2879
Aliases: CVE-2022-2879, GO-2022-1037
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-2879
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.19.0 <1.19.2

## Details
Reader.Read does not set a limit on the maximum size of file headers. A maliciously crafted archive could cause Read to allocate unbounded amounts of memory, potentially causing resource exhaustion or panics. After fix, Reader.Read limits the maximum size of header blocks to 1 MiB.

## References
- https://go.dev/cl/439355
- https://go.dev/issue/54853
- https://groups.google.com/g/golang-announce/c/xtuG5faxtaU
- https://pkg.go.dev/vuln/GO-2022-1037
- https://security.gentoo.org/glsa/202311-09
- https://nvd.nist.gov/vuln/detail/CVE-2022-2879
