# [M] JLSEC-2026-901

## Summary
Severity: Medium
Advisory: JLSEC-2026-901
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-901
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.1+0

## Details
A vulnerability was discovered in ImageMagick where a specially created SVG file loads itself and causes a segmentation fault. This flaw allows a remote attacker to pass a specially crafted SVG file that leads to a segmentation fault, generating many trash files in "`/tmp`," resulting in a denial of service. When ImageMagick crashes, it generates a lot of trash files. These trash files can be large if the SVG file contains many render actions. In a denial of service attack, if a remote attacker uploads an SVG file of size t, ImageMagick generates files of size 103*t. If an attacker uploads a 100M SVG, the server will generate about 10G.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2176858
- https://bugzilla.redhat.com/show_bug.cgi?id=2176858
- https://github.com/ImageMagick/ImageMagick/commit/c5b23cbf2119540725e6dc81f4deb25798ead6a4
- https://github.com/ImageMagick/ImageMagick/commit/c5b23cbf2119540725e6dc81f4deb25798ead6a4
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-j96m-mjp6-99xr
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-j96m-mjp6-99xr
- https://lists.debian.org/debian-lts-announce/2024/02/msg00007.html
- https://lists.debian.org/debian-lts-announce/2024/02/msg00007.html
