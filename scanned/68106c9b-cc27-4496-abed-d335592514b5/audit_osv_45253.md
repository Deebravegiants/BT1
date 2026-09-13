# [M] Reachable Assertion in tiffcp in libtiff 4.3.0 allows attackers to cause a denial-of-service via a...

## Summary
Severity: Medium
Advisory: JLSEC-2025-262
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-262
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=4.3.0+0 <4.4.0+0

## Details
Reachable Assertion in tiffcp in libtiff 4.3.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit 5e180045.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0865.json
- https://gitlab.com/libtiff/libtiff/-/issues/385
- https://gitlab.com/libtiff/libtiff/-/merge_requests/306
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNT2GFNRLOMKJ5KXM6JIHKBNBFDVZPD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ4E654ZYUUUQNBKYQFXNK2CV3CPWTM2/
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20221228-0008/
- https://www.debian.org/security/2022/dsa-5108
