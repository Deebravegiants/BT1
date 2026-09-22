# [H] CVE-2019-6247

## Summary
Severity: High
Advisory: CVE-2019-6247
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-01-13
Source: https://osv.dev/vulnerability/CVE-2019-6247
Type: osv

## Details
An issue was discovered in Anti-Grain Geometry (AGG) 2.4 as used in SVG++ (aka svgpp) 1.2.3. A heap-based buffer overflow bug in svgpp_agg_render may lead to code execution. In the render_scanlines_aa_solid function, the blend_hline function is called repeatedly multiple times. blend_hline is equivalent to a loop containing write operations. Each call writes a piece of heap data, and multiple calls overwrite the data in the heap.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00001.html
- https://github.com/svgpp/svgpp/issues/70
