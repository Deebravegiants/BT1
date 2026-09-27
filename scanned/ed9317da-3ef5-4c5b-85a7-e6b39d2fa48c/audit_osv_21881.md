# [H] CVE-2022-0908

## Summary
Severity: High
Advisory: CVE-2022-0908
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-03-11
Source: https://osv.dev/vulnerability/CVE-2022-0908
Type: osv

## Details
Null source pointer passed as an argument to memcpy() function within TIFFFetchNormalTag () in tif_dirread.c in libtiff versions up to 4.3.0 could lead to Denial of Service via crafted TIFF file.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0908.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0908.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNT2GFNRLOMKJ5KXM6JIHKBNBFDVZPD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ4E654ZYUUUQNBKYQFXNK2CV3CPWTM2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0908
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220506-0002/
- https://www.debian.org/security/2022/dsa-5108
- https://gitlab.com/libtiff/libtiff/-/issues/383
- https://gitlab.com/libtiff/libtiff/-/commit/a95b799f65064e4ba2e2dfc206808f86faf93e85
