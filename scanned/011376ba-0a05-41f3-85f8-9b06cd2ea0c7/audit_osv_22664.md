# [M] CVE-2022-3599

## Summary
Severity: Medium
Advisory: CVE-2022-3599
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3599
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds read in writeSingleSection in tools/tiffcrop.c:7345, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit e8131125.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3599.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3599.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3599
- https://security.netapp.com/advisory/ntap-20230110-0001/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/398
- https://gitlab.com/libtiff/libtiff/-/commit/e813112545942107551433d61afd16ac094ff246
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
