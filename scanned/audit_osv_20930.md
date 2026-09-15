# [H] CVE-2021-38593

## Summary
Severity: High
Advisory: CVE-2021-38593
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-38593
Type: osv

## Details
Qt 5.x before 5.15.6 and 6.x through 6.1.2 has an out-of-bounds write in QOutlineMapper::convertPath (called from QRasterPaintEngine::fill and QPaintEngineEx::stroke).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36VN2WKMNQUSTF6ZW2X52NPAJVXJ4S5I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HY5YCSDCTLHVMP3OXOM6HNTWHV6DBHDX/
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/qt/OSV-2021-903.yaml
- https://security.gentoo.org/glsa/202402-03
- https://www.qt.io/blog/qt-5.15-extended-support-for-subscription-license-holders
- https://wiki.qt.io/Qt_5.15_Release#Known_Issues
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=35566
- https://github.com/qt/qtbase/commit/1ca02cf2879a5e1511a2f2109f0925cf4c892862
- https://github.com/qt/qtbase/commit/202143ba41f6ac574f1858214ed8bf4a38b73ccd
- https://github.com/qt/qtbase/commit/6b400e3147dcfd8cc3a393ace1bd118c93762e0c
