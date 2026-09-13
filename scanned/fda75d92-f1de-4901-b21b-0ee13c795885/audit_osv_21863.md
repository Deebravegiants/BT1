# [M] CVE-2022-0562

## Summary
Severity: Medium
Advisory: CVE-2022-0562
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-11
Source: https://osv.dev/vulnerability/CVE-2022-0562
Type: osv

## Details
Null source pointer passed as an argument to memcpy() function within TIFFReadDirectory() in tif_dirread.c in libtiff versions from 4.0 to 4.3.0 could lead to Denial of Service via crafted TIFF file. For users that compile libtiff from sources, a fix is available with commit 561599c.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0562.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0562.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DZEHZ35XVO2VBZ4HHCMM6J6TQIDSBQOM/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0562
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220318-0001/
- https://www.debian.org/security/2022/dsa-5108
- https://gitlab.com/libtiff/libtiff/-/issues/362
- https://gitlab.com/gitlab-org/build/omnibus-mirror/libtiff/-/commit/561599c99f987dc32ae110370cfdd7df7975586b
- https://lists.debian.org/debian-lts-announce/2022/03/msg00001.html
