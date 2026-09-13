# [M] CVE-2022-48281

## Summary
Severity: Medium
Advisory: CVE-2022-48281
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-23
Source: https://osv.dev/vulnerability/CVE-2022-48281
Type: osv

## Details
processCropSelections in tools/tiffcrop.c in LibTIFF through 4.5.0 has a heap-based buffer overflow (e.g., "WRITE of size 307203") via a crafted TIFF image.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48281.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48281
- https://security.gentoo.org/glsa/202305-31
- https://security.netapp.com/advisory/ntap-20230302-0004/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/488
- https://gitlab.com/libtiff/libtiff/-/commit/d1b6b9c1b3cae2d9e37754506c1ad8f4f7b646b5
- https://lists.debian.org/debian-lts-announce/2023/01/msg00037.html
