# [M] CVE-2023-0801

## Summary
Severity: Medium
Advisory: CVE-2023-0801
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-02-13
Source: https://osv.dev/vulnerability/CVE-2023-0801
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds write in tiffcrop in libtiff/tif_unix.c:368, invoked by tools/tiffcrop.c:2903 and tools/tiffcrop.c:6778, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 33aee127.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0801.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0801.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0801
- https://security.gentoo.org/glsa/202305-31
- https://security.netapp.com/advisory/ntap-20230316-0002/
- https://www.debian.org/security/2023/dsa-5361
- https://gitlab.com/libtiff/libtiff/-/issues/498
- https://gitlab.com/libtiff/libtiff/-/commit/33aee1275d9d1384791d2206776eb8152d397f00
- https://lists.debian.org/debian-lts-announce/2023/02/msg00026.html
