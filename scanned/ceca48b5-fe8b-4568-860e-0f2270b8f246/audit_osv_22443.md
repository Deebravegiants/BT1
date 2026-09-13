# [M] CVE-2022-2953

## Summary
Severity: Medium
Advisory: CVE-2022-2953
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-2953
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds read in extractImageSection in tools/tiffcrop.c:6905, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 48d6ece8.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2953.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2953.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2953
- https://security.netapp.com/advisory/ntap-20221014-0008/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/414
- https://gitlab.com/libtiff/libtiff/-/commit/48d6ece8389b01129e7d357f0985c8f938ce3da3
