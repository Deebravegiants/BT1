# [H] CVE-2020-36279

## Summary
Severity: High
Advisory: CVE-2020-36279
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-12
Source: https://osv.dev/vulnerability/CVE-2020-36279
Type: osv

## Details
Leptonica before 1.80.0 allows a heap-based buffer over-read in rasteropGeneralLow, related to adaptmap_reg.c and adaptmap.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RD5AIWHWE334HGYZJR2U3I3JYKSSO2LW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQUEA2X6UTH4DMYCMZAWE2QQLN5YANUA/
- https://security.gentoo.org/glsa/202107-53
- https://lists.debian.org/debian-lts-announce/2021/03/msg00037.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=22512
- https://github.com/DanBloomberg/leptonica/commit/3c18c43b6a3f753f0dfff99610d46ad46b8bfac4
- https://github.com/DanBloomberg/leptonica/compare/1.79.0...1.80.0
