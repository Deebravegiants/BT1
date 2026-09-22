# [C] WPG in GraphicsMagick before 1.3.46 mishandles palette buffer allocation.

## Summary
Severity: Critical
Advisory: JLSEC-2026-494
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/JLSEC-2026-494
Type: osv

## Affected
- Julia: `GraphicsMagick_jll` — affected >=0 <1.3.47+0

## Details
ReadWPGImage in WPG in GraphicsMagick before 1.3.46 mishandles palette buffer allocation, resulting in out-of-bounds access to heap memory in ReadBlob.

## References
- http://www.graphicsmagick.org/NEWS.html
- https://foss.heptapod.net/graphicsmagick/graphicsmagick/-/commit/883ebf8cae6dfa5873d975fe3476b1a188ef3f9f
- https://github.com/advisories/GHSA-v5xf-gj23-85jx
- https://nvd.nist.gov/vuln/detail/CVE-2025-27796
- https://sourceforge.net/p/graphicsmagick/bugs/750
- https://sourceforge.net/p/graphicsmagick/bugs/750/
