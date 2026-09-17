# [H] CVE-2022-3570

## Summary
Severity: High
Advisory: CVE-2022-3570
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3570
Type: osv

## Details
Multiple heap buffer overflows in tiffcrop.c utility in libtiff library Version 4.4.0 allows attacker to trigger unsafe or out of bounds memory access via crafted TIFF image file which could result into application crash, potential information disclosure or any other context-dependent impact

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3570.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3570.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3570
- https://security.netapp.com/advisory/ntap-20230203-0002/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/381
- https://gitlab.com/libtiff/libtiff/-/issues/386
- https://gitlab.com/libtiff/libtiff/-/commit/bd94a9b383d8755a27b5a1bc27660b8ad10b094c
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
