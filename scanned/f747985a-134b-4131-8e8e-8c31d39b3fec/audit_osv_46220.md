# [M] JLSEC-2026-83

## Summary
Severity: Medium
Advisory: JLSEC-2026-83
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/JLSEC-2026-83
Type: osv

## Affected
- Julia: `Poppler_jll` — affected >=0 <25.10.0+0

## Details
libpoppler.so in Poppler through 24.12.0 has an out-of-bounds read vulnerability within the JBIG2Bitmap::combine function in JBIG2Stream.cc.

## References
- https://gitlab.freedesktop.org/poppler/poppler/-/blob/30eada0d2bceb42c2d2a87361339063e0b9bea50/CMakeLists.txt#L621
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/ade9b5ebed44b0c15522c27669ef6cdf93eff84e
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1553
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
