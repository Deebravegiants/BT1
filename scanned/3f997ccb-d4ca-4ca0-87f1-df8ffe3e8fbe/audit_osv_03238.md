# [H] ALPINE-CVE-2025-27363

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-27363
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27363
Type: osv

## Affected
- Alpine:v3.22: `freetype` — affected >=0 <2.13.1-r0
- Alpine:v3.23: `freetype` — affected >=0 <2.13.1-r0
- Alpine:v3.24: `freetype` — affected >=0 <2.13.1-r0

## Details
An out of bounds write exists in FreeType versions 2.13.0 and below (newer versions of FreeType are not vulnerable) when attempting to parse font subglyph structures related to TrueType GX and variable font files. The vulnerable code assigns a signed short value to an unsigned long and then adds a static value causing it to wrap around and allocate too small of a heap buffer. The code then writes up to 6 signed long integers out of bounds relative to this buffer. This may result in arbitrary code execution. This vulnerability may have been exploited in the wild.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27363
