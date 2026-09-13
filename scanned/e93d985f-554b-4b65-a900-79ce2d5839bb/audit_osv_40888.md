# [H] libXfont2 PCF Font Parsing Heap Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-56002
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56002
Type: osv

## Details
A heap bufferflow in pcfReadFont() due to missing glyph bounds checking in libXfont2 before 2.0.8  allows attackers authenticated as X client to execute code within the X server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56002
- https://www.openwall.com/lists/oss-security/2026/07/08/1
- https://gitlab.freedesktop.org/xorg/lib/libxfont/-/commit/b4389e0b1d84a690b819bb27b1439968811a3674
- https://gitlab.freedesktop.org/xorg/lib/libxfont
