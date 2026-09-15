# [M] CVE-2022-4645

## Summary
Severity: Medium
Advisory: CVE-2022-4645
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2023-03-03
Source: https://osv.dev/vulnerability/CVE-2022-4645
Type: osv

## Details
LibTIFF 4.4.0 has an out-of-bounds read in tiffcp in tools/tiffcp.c:948, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit e8131125.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4645.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4645.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2ZTFA6GGOKFPIQNHDBMXYUR4XUXUJESE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BA6GRCAQ7NR2OK5N44UQRGUJBIYKWJJH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OLM763GGZVVOAXIQXG6YGTYJ5VFYNECQ/
- https://nvd.nist.gov/vuln/detail/CVE-2022-4645
- https://security.netapp.com/advisory/ntap-20230331-0001/
- https://gitlab.com/libtiff/libtiff/-/issues/277
- https://gitlab.com/libtiff/libtiff/-/commit/e813112545942107551433d61afd16ac094ff246
