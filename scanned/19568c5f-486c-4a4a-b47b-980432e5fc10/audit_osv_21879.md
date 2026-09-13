# [M] CVE-2022-0891

## Summary
Severity: Medium
Advisory: CVE-2022-0891
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-03-09
Source: https://osv.dev/vulnerability/CVE-2022-0891
Type: osv

## Details
A heap buffer overflow in ExtractImageSection function in tiffcrop.c in libtiff library Version 4.3.0 allows attacker to trigger unsafe or out of bounds memory access via crafted TIFF image file which could result into application crash, potential information disclosure or any other context-dependent impact

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0891.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/0xxx/CVE-2022-0891.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNT2GFNRLOMKJ5KXM6JIHKBNBFDVZPD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ4E654ZYUUUQNBKYQFXNK2CV3CPWTM2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-0891
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20221228-0008/
- https://www.debian.org/security/2022/dsa-5108
- https://gitlab.com/libtiff/libtiff/-/issues/380
- https://gitlab.com/libtiff/libtiff/-/issues/382
- https://gitlab.com/freedesktop-sdk/mirrors/gitlab/libtiff/libtiff/-/commit/232282fd8f9c21eefe8d2d2b96cdbbb172fe7b7c
