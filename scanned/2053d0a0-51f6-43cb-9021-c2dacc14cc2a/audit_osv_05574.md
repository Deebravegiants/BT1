# [M] BIT-golang-2021-3114

## Summary
Severity: Medium
Advisory: BIT-golang-2021-3114
Aliases: CVE-2021-3114, GO-2021-0235
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-3114
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.15.0 <1.15.7

## Details
In Go before 1.14.14 and 1.15.x before 1.15.7, crypto/elliptic/p224.go can generate incorrect outputs, related to an underflow of the lowest limb during the final complete reduction in the P-224 field.

## References
- https://github.com/golang/go/commit/d95ca9138026cbe40e0857d76a81a16d03230871
- https://groups.google.com/g/golang-announce/c/mperVMGa98w
- https://lists.debian.org/debian-lts-announce/2021/03/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YWAYJGXWC232SG3UR3TR574E6BP3OSQQ/
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20210219-0001/
- https://www.debian.org/security/2021/dsa-4848
- https://nvd.nist.gov/vuln/detail/CVE-2021-3114
