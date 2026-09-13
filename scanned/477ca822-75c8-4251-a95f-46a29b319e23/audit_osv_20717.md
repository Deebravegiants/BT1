# [M] CVE-2021-36410

## Summary
Severity: Medium
Advisory: CVE-2021-36410
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-36410
Type: osv

## Details
A stack-buffer-overflow exists in libde265 v1.0.8 via fallback-motion.cc in function put_epel_hv_fallback when running program dec265.

## References
- https://github.com/strukturag/libde265/issues/301
- https://lists.debian.org/debian-lts-announce/2022/12/msg00027.html
- https://www.debian.org/security/2023/dsa-5346
