# [H] BIT-java-2026-41254

## Summary
Severity: High
Advisory: BIT-java-2026-41254
Aliases: BIT-java-min-2026-41254, BIT-jre-2026-41254, CVE-2026-41254, GHSA-4xp6-rcgg-m9qq
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-java-2026-41254
Type: osv

## Affected
- Bitnami: `java` — affected >=26.0.0 <26.0.2

## Details
Little CMS (lcms2) through 2.18 has an integer overflow in CubeSize in cmslut.c because the overflow check is performed after the multiplication.

## References
- https://abhinavagarwal07.github.io/posts/lcms2-cubesize-overflow/
- https://github.com/mm2/Little-CMS/commit/da6110b1d14abc394633a388209abd5ebedd7ab0
- https://github.com/mm2/Little-CMS/commit/e0641b1828d0a1af5ecb1b11fe22f24fceefd4bc
- https://github.com/mm2/Little-CMS/commit/e0641b1828d0a1af5ecb1b11fe22f24fceefd4bc#commitcomment-183284136
- https://github.com/mm2/Little-CMS/security/advisories/GHSA-4xp6-rcgg-m9qq
- https://lists.debian.org/debian-lts-announce/2026/05/msg00014.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-41254
- https://openjdk.org/groups/vulnerability/advisories/2026-07-21
- https://www.openwall.com/lists/oss-security/2026/04/17/16
