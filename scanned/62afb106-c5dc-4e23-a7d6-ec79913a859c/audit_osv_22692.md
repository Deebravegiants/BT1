# [M] CVE-2022-3627

## Summary
Severity: Medium
Advisory: CVE-2022-3627
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3627
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds write in _TIFFmemcpy in libtiff/tif_unix.c:346 when called from extractImageSection, tools/tiffcrop.c:6860, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 236b7191.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3627.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3627.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3627
- https://security.netapp.com/advisory/ntap-20230110-0001/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/411
- https://gitlab.com/libtiff/libtiff/-/commit/236b7191f04c60d09ee836ae13b50f812c841047
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
