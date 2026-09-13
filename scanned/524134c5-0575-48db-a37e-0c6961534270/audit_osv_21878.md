# [M] CVE-2022-0865

## Summary
Severity: Medium
Advisory: CVE-2022-0865
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-07
Source: https://osv.dev/vulnerability/CVE-2022-0865
Type: osv

## Details
Reachable Assertion in tiffcp in libtiff 4.3.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 5e180045.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0865.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0865.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNT2GFNRLOMKJ5KXM6JIHKBNBFDVZPD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ4E654ZYUUUQNBKYQFXNK2CV3CPWTM2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0865
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20221228-0008/
- https://www.debian.org/security/2022/dsa-5108
- https://gitlab.com/libtiff/libtiff/-/issues/385
- https://gitlab.com/libtiff/libtiff/-/merge_requests/306
