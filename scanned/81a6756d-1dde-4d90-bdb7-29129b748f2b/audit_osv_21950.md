# [M] CVE-2022-1623

## Summary
Severity: Medium
Advisory: CVE-2022-1623
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-05-11
Source: https://osv.dev/vulnerability/CVE-2022-1623
Type: osv

## Details
LibTIFF master branch has an out-of-bounds read in LZWDecode in libtiff/tif_lzw.c:624, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit b4e79bfa.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1623.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1623.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7IWZTB4J2N4F5OR5QY4VHDSKWKZSWN3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UXAFOP6QQRNZD3HPZ6BMCEZZOM4YIZMK/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1623
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220616-0005/
- https://www.debian.org/security/2023/dsa-5333
- https://gitlab.com/libtiff/libtiff/-/issues/410
- https://gitlab.com/libtiff/libtiff/-/commit/b4e79bfa0c7d2d08f6f1e7ec38143fc8cb11394a
