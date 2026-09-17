# [M] CVE-2021-45930

## Summary
Severity: Medium
Advisory: CVE-2021-45930
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45930
Type: osv

## Details
Qt SVG in Qt 5.0.0 through 5.15.2 and 6.0.0 through 6.2.1 has an out-of-bounds write in QtPrivate::QCommonArrayOps<QPainterPath::Element>::growAppend (called from QPainterPath::addPath and QPathClipper::intersect).

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4GKOKVCSDZSOWWR3HOW5XUIUJC4MKQY5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GZIXNSX7FV733TWTTLY6FHSH3SCNQKKD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/V75XNX4GDB64N5BSOAN474RUXXS5OHRU/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00020.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00022.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=37025
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=37306
- https://github.com/qt/qtsvg/commit/36cfd9efb9b22b891adee9c48d30202289cfa620
- https://github.com/qt/qtsvg/commit/79bb9f51fa374106a612d17c9d98d35d807be670
- https://github.com/qt/qtsvg/commit/a3b753c2d077313fc9eb93af547051b956e383fc
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/qt/OSV-2021-1121.yaml
