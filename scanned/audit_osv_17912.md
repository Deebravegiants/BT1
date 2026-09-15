# [M] CVE-2020-21599

## Summary
Severity: Medium
Advisory: CVE-2020-21599
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-16
Source: https://osv.dev/vulnerability/CVE-2020-21599
Type: osv

## Details
libde265 v1.0.4 contains a heap buffer overflow in the de265_image::available_zscan function, which can be exploited via a crafted a file.

## References
- https://github.com/strukturag/libde265/issues/235
- https://lists.debian.org/debian-lts-announce/2022/12/msg00027.html
- https://www.debian.org/security/2023/dsa-5346
