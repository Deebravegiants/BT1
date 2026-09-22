# [M] BIT-golang-2021-44717

## Summary
Severity: Medium
Advisory: BIT-golang-2021-44717
Aliases: CVE-2021-44717, GO-2022-0289
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-44717
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.17.0 <1.17.5

## Details
Go before 1.16.12 and 1.17.x before 1.17.5 on UNIX allows write operations to an unintended file or unintended network connection as a consequence of erroneous closing of file descriptor 0 after file-descriptor exhaustion.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-744259.pdf
- https://groups.google.com/g/golang-announce/c/hcmEScgc00k
- https://lists.debian.org/debian-lts-announce/2022/01/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00017.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00021.html
- https://security.gentoo.org/glsa/202208-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-44717
