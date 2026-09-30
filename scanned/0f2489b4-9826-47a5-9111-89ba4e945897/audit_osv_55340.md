# [C] CVE-2025-32460

## Summary
Severity: Critical
Advisory: CVE-2025-32460
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-09
Source: https://osv.dev/vulnerability/CVE-2025-32460
Type: osv

## Details
GraphicsMagick before 8e56520 has a heap-based buffer over-read in ReadJXLImage in coders/jxl.c, related to an ImportViewPixelArea call.

## References
- https://foss.heptapod.net/graphicsmagick/graphicsmagick/-/commit/8e56520435df50f618a03f2721a39a70a515f1cb
- https://issues.oss-fuzz.com/issues/406320404
- https://tracker.debian.org/news/1636753/accepted-graphicsmagick-14really1345hg17696-1-source-into-unstable/
