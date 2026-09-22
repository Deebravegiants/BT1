# [M] JLSEC-2026-845

## Summary
Severity: Medium
Advisory: JLSEC-2026-845
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-845
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <6.9.12+0

## Details
WriteOnePNGImage() from `coders/png.c` (the PNG coder) has a for loop with an improper exit condition that can allow an out-of-bounds READ via heap-buffer-overflow. This occurs because it is possible for the colormap to have less than 256 valid values but the loop condition will loop 256 times, attempting to pass invalid colormap data to the event logger. The patch replaces the hardcoded 256 value with a call to MagickMin() to ensure the proper value is used. This could impact application availability when a specially crafted input file is processed by ImageMagick. This flaw affects ImageMagick versions prior to 7.0.8-68.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1891928
- https://bugzilla.redhat.com/show_bug.cgi?id=1891928
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/03/msg00008.html
