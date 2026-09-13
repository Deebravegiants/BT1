# [M] LibTIFF 4.4.0 has an out-of-bounds read in tiffcp in `tools/tiffcp.c:948`, allowing attackers to...

## Summary
Severity: Medium
Advisory: JLSEC-2025-300
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-300
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
LibTIFF 4.4.0 has an out-of-bounds read in tiffcp in `tools/tiffcp.c:948`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit e8131125.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4645.json
- https://gitlab.com/libtiff/libtiff/-/commit/e813112545942107551433d61afd16ac094ff246
- https://gitlab.com/libtiff/libtiff/-/issues/277
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2ZTFA6GGOKFPIQNHDBMXYUR4XUXUJESE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BA6GRCAQ7NR2OK5N44UQRGUJBIYKWJJH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OLM763GGZVVOAXIQXG6YGTYJ5VFYNECQ/
- https://security.netapp.com/advisory/ntap-20230331-0001/
