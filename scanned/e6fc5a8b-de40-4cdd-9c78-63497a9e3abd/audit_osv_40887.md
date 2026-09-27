# [H] libXfont2 BitmapScaleBitmaps Integer Overflow Heap Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-56001
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56001
Type: osv

## Details
A heap buffer overflow in BitmapScaleBitmaps in libXfont2 before 2.0.8 due to an overflowing 32bit size could be used by attackers able to access the X Server to execute code within the X server cont

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56001.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56001
- https://www.openwall.com/lists/oss-security/2026/07/08/1
- https://gitlab.freedesktop.org/xorg/lib/libxfont/-/commit/be0b08e2d354138d3222b4490e2a77c6ee42f778
- https://gitlab.freedesktop.org/xorg/lib/libxfont
