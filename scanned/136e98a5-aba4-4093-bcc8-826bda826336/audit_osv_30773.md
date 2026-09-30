# [M] CVE-2024-56378

## Summary
Severity: Medium
Advisory: CVE-2024-56378
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-12-22
Source: https://osv.dev/vulnerability/CVE-2024-56378
Type: osv

## Details
libpoppler.so in Poppler through 24.12.0 has an out-of-bounds read vulnerability within the JBIG2Bitmap::combine function in JBIG2Stream.cc.

## References
- https://gitlab.freedesktop.org/poppler/poppler/-/blob/30eada0d2bceb42c2d2a87361339063e0b9bea50/CMakeLists.txt#L621
- https://lists.debian.org/debian-lts-announce/2025/04/msg00037.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56378.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56378
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1553
- https://gitlab.freedesktop.org/poppler/poppler/-/commit/ade9b5ebed44b0c15522c27669ef6cdf93eff84e
