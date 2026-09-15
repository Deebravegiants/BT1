# [C] GraphicsMagick before 8e56520 has a heap-based buffer over-read in ReadJXLImage in `coders/jxl.c`,...

## Summary
Severity: Critical
Advisory: JLSEC-2026-495
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/JLSEC-2026-495
Type: osv

## Affected
- Julia: `GraphicsMagick_jll` — affected >=0 <1.3.47+0

## Details
GraphicsMagick before 8e56520 has a heap-based buffer over-read in ReadJXLImage in `coders/jxl.c`, related to an ImportViewPixelArea call.

## References
- https://foss.heptapod.net/graphicsmagick/graphicsmagick/-/commit/8e56520435df50f618a03f2721a39a70a515f1cb
- https://github.com/advisories/GHSA-hf7q-qx98-4hm7
- https://issues.oss-fuzz.com/issues/406320404
- https://nvd.nist.gov/vuln/detail/CVE-2025-32460
- https://tracker.debian.org/news/1636753/accepted-graphicsmagick-14really1345hg17696-1-source-into-unstable
- https://tracker.debian.org/news/1636753/accepted-graphicsmagick-14really1345hg17696-1-source-into-unstable/
