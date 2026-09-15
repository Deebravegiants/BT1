# [H] JLSEC-2026-491

## Summary
Severity: High
Advisory: JLSEC-2026-491
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/JLSEC-2026-491
Type: osv

## Affected
- Julia: `LittleCMS_jll` — affected >=0 <2.19.0+0

## Details
Little CMS (lcms2) through 2.18 has an integer overflow in CubeSize in cmslut.c because the overflow check is performed after the multiplication.

## References
- https://abhinavagarwal07.github.io/posts/lcms2-cubesize-overflow/
- https://github.com/mm2/Little-CMS/commit/da6110b1d14abc394633a388209abd5ebedd7ab0
- https://github.com/mm2/Little-CMS/commit/e0641b1828d0a1af5ecb1b11fe22f24fceefd4bc
- https://github.com/mm2/Little-CMS/security/advisories/GHSA-4xp6-rcgg-m9qq
- https://lists.debian.org/debian-lts-announce/2026/05/msg00014.html
- https://www.openwall.com/lists/oss-security/2026/04/17/16
