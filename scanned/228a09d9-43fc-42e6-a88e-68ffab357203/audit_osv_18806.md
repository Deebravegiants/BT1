# [H] CVE-2020-36277

## Summary
Severity: High
Advisory: CVE-2020-36277
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2020-36277
Type: osv

## Details
Leptonica before 1.80.0 allows a denial of service (application crash) via an incorrect left shift in pixConvert2To8 in pixconv.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQUEA2X6UTH4DMYCMZAWE2QQLN5YANUA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RD5AIWHWE334HGYZJR2U3I3JYKSSO2LW/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00037.html
- https://security.gentoo.org/glsa/202107-53
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=21997
- https://github.com/DanBloomberg/leptonica/pull/499
- https://github.com/DanBloomberg/leptonica/compare/1.79.0...1.80.0
