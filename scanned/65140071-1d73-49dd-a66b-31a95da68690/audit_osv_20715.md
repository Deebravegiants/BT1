# [M] CVE-2021-36408

## Summary
Severity: Medium
Advisory: CVE-2021-36408
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-36408
Type: osv

## Details
An issue was discovered in libde265 v1.0.8.There is a Heap-use-after-free in intrapred.h when decoding file using dec265.

## References
- https://github.com/strukturag/libde265/issues/299
- https://lists.debian.org/debian-lts-announce/2022/12/msg00027.html
- https://www.debian.org/security/2023/dsa-5346
