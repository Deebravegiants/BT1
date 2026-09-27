# [M] CVE-2020-21603

## Summary
Severity: Medium
Advisory: CVE-2020-21603
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-16
Source: https://osv.dev/vulnerability/CVE-2020-21603
Type: osv

## Details
libde265 v1.0.4 contains a heap buffer overflow in the put_qpel_0_0_fallback_16 function, which can be exploited via a crafted a file.

## References
- https://www.debian.org/security/2023/dsa-5346
- https://github.com/strukturag/libde265/issues/240
