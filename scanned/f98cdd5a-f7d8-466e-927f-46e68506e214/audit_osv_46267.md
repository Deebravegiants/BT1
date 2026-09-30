# [H] JLSEC-2026-899

## Summary
Severity: High
Advisory: JLSEC-2026-899
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-899
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+3

## Details
A vulnerability was found in ImageMagick, causing an outside the range of representable values of type 'unsigned long' at `coders/pcl.c`, when crafted or untrusted input is processed. This leads to a negative impact to application availability or other problems related to undefined behavior.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2091812
- https://bugzilla.redhat.com/show_bug.cgi?id=2091812
- https://github.com/ImageMagick/ImageMagick/commit/f221ea0fa3171f0f4fdf74ac9d81b203b9534c23
- https://github.com/ImageMagick/ImageMagick/commit/f221ea0fa3171f0f4fdf74ac9d81b203b9534c23
- https://github.com/ImageMagick/ImageMagick6/commit/29c8abce0da56b536542f76a9ddfebdaab5b2943
- https://github.com/ImageMagick/ImageMagick6/commit/29c8abce0da56b536542f76a9ddfebdaab5b2943
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00020.html
