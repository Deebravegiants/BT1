# [M] CVE-2021-36411

## Summary
Severity: Medium
Advisory: CVE-2021-36411
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-36411
Type: osv

## Details
An issue has been found in libde265 v1.0.8 due to incorrect access control. A SEGV caused by a READ memory access in function derive_boundaryStrength of deblock.cc has occurred. The vulnerability causes a segmentation fault and application crash, which leads to remote denial of service.

## References
- https://github.com/strukturag/libde265/issues/302
- https://lists.debian.org/debian-lts-announce/2022/12/msg00027.html
- https://www.debian.org/security/2023/dsa-5346
