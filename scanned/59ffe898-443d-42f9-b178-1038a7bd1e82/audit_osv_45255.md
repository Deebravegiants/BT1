# [M] Divide By Zero error in tiffcrop in libtiff 4.3.0 allows attackers to cause a denial-of-service via...

## Summary
Severity: Medium
Advisory: JLSEC-2025-266
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-266
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=4.3.0+0 <4.4.0+0

## Details
Divide By Zero error in tiffcrop in libtiff 4.3.0 allows attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit f8d0f9aa.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0909.json
- https://gitlab.com/libtiff/libtiff/-/issues/393
- https://gitlab.com/libtiff/libtiff/-/merge_requests/310
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RNT2GFNRLOMKJ5KXM6JIHKBNBFDVZPD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ4E654ZYUUUQNBKYQFXNK2CV3CPWTM2/
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220506-0002/
- https://www.debian.org/security/2022/dsa-5108
