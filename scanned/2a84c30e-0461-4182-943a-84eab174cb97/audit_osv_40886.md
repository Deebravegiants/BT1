# [H] xorg-server / xwayland glamor font atlas Heap Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-55999
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-55999
Type: osv

## Details
Local attackers with a X connection able to provide PCX fonts to the X 
server xorg-server before 21.2.24 and xwayland before 24.1.13 could 
cause a heap buffer overflow via SetFont due to missing glyph boundary checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55999
- https://www.openwall.com/lists/oss-security/2026/07/08/2
- https://gitlab.freedesktop.org/xorg/xserver/-/commit/fbf7bac22e2c6bd627fb042742a23318263edae1
- https://gitlab.freedesktop.org/xorg/xserver/
