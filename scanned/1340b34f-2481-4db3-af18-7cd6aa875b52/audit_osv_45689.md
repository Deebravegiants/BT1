# [H] JLSEC-2026-207

## Summary
Severity: High
Advisory: JLSEC-2026-207
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-207
Type: osv

## Affected
- Julia: `Leptonica_jll` — affected >=0 <1.81.1+0

## Details
Leptonica before 1.80.0 allows a heap-based buffer over-read in rasteropGeneralLow, related to `adaptmap_reg.c` and adaptmap.c.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=22512
- https://github.com/DanBloomberg/leptonica/commit/3c18c43b6a3f753f0dfff99610d46ad46b8bfac4
- https://github.com/DanBloomberg/leptonica/compare/1.79.0...1.80.0
- https://lists.debian.org/debian-lts-announce/2021/03/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JQUEA2X6UTH4DMYCMZAWE2QQLN5YANUA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RD5AIWHWE334HGYZJR2U3I3JYKSSO2LW/
- https://security.gentoo.org/glsa/202107-53
