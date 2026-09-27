# [M] CVE-2023-0804

## Summary
Severity: Medium
Advisory: CVE-2023-0804
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-02-13
Source: https://osv.dev/vulnerability/CVE-2023-0804
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds write in tiffcrop in tools/tiffcrop.c:3609, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 33aee127.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-0804.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0804.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FBF3UUFSB6NB3NFTQSKOOIZGXJP3T34Z/
- https://nvd.nist.gov/vuln/detail/CVE-2023-0804
- https://security.gentoo.org/glsa/202305-31
- https://security.netapp.com/advisory/ntap-20230324-0009/
- https://www.debian.org/security/2023/dsa-5361
- https://gitlab.com/libtiff/libtiff/-/issues/497
- https://gitlab.com/libtiff/libtiff/-/commit/33aee1275d9d1384791d2206776eb8152d397f00
- https://lists.debian.org/debian-lts-announce/2023/02/msg00026.html
