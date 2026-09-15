# [H] GNU Emacs < 31.0.91 Heap Over-Read via PBM/PPM/PGM Image Loader

## Summary
Severity: High
Advisory: CVE-2026-77219
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77219
Type: osv

## Details
GNU Emacs before 31.0.91 contains an integer overflow in the PBM/PPM/PGM image loader that allows an attacker to leak heap memory contents by supplying a crafted image with large dimensions and an elevated max color index. The image loader multiplies image dimensions and channel count using signed integer arithmetic; for sufficiently large values, the result wraps to a negative number, bypassing the bounds check and causing the pixel reader to access heap memory past the end of the allocated buffer. The over-read contents are interpreted as pixel color values and rendered on screen.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77219.json
- https://github.com/emacs-mirror/emacs/releases/tag/emacs-31.0.91
- https://nvd.nist.gov/vuln/detail/CVE-2026-77219
- https://www.vulncheck.com/advisories/gnu-emacs-heap-over-read-via-pbm-ppm-pgm-image-loader
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=81344
- https://github.com/emacs-mirror/emacs/commit/b07e634e4cf45162ae0178e32092b040587f2c6c
- https://github.com/emacs-mirror/emacs
