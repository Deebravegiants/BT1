# [H] libXfont2 computeProps Property Buffer Heap Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2026-56003
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56003
Type: osv

## Details
A heap buffer overflow due to missing size checking in the property buffer when parsing PCF files in libXfont2 ComputeScaledProperties() before libXfont2 before 2.0.8 could be used by attackers using authenticated X clients to execute code within the X server.

## References
- https://gitlab.freedesktop.org/xorg/lib/libxfont/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56003.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56003
- https://www.openwall.com/lists/oss-security/2026/07/08/1
- https://gitlab.freedesktop.org/xorg/lib/libxfont/-/commit/dff957a5158da038a282a59a31fe736702732939
