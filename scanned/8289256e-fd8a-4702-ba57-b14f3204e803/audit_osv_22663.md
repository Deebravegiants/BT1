# [M] CVE-2022-3598

## Summary
Severity: Medium
Advisory: CVE-2022-3598
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-3598
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds write in extractContigSamplesShifted24bits in tools/tiffcrop.c:3604, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit cfbb883b.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3598.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3598.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3598
- https://security.netapp.com/advisory/ntap-20230110-0001/
- https://gitlab.com/libtiff/libtiff/-/issues/435
- https://gitlab.com/libtiff/libtiff/-/commit/cfbb883bf6ea7bedcb04177cc4e52d304522fdff
- https://lists.debian.org/debian-lts-announce/2023/01/msg00018.html
