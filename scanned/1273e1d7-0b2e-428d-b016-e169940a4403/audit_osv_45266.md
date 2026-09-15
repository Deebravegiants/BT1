# [M] Multiple heap buffer overflows in tiffcrop.c utility in libtiff library Version 4.4.0 allows...

## Summary
Severity: Medium
Advisory: JLSEC-2025-282
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-282
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
Multiple heap buffer overflows in tiffcrop.c utility in libtiff library Version 4.4.0 allows attacker to trigger unsafe or out of bounds memory access via crafted TIFF image file which could result into application crash, potential information disclosure or any other context-dependent impact

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3570.json
- https://gitlab.com/libtiff/libtiff/-/commit/bd94a9b383d8755a27b5a1bc27660b8ad10b094c
- https://gitlab.com/libtiff/libtiff/-/issues/381
- https://gitlab.com/libtiff/libtiff/-/issues/386
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
- https://security.netapp.com/advisory/ntap-20230203-0002/
- https://www.debian.org/security/2023/dsa-5333
