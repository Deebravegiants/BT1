# [M] CVE-2022-0907

## Summary
Severity: Medium
Advisory: CVE-2022-0907
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-11
Source: https://osv.dev/vulnerability/CVE-2022-0907
Type: osv

## Details
Unchecked Return Value to NULL Pointer Dereference in tiffcrop in libtiff 4.3.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit f2b656e2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0907.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0907.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNT2GFNRLOMKJ5KXM6JIHKBNBFDVZPD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ4E654ZYUUUQNBKYQFXNK2CV3CPWTM2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0907
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220506-0002/
- https://www.debian.org/security/2022/dsa-5108
- https://gitlab.com/libtiff/libtiff/-/issues/392
- https://gitlab.com/libtiff/libtiff/-/merge_requests/314
