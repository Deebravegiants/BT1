# [M] FreeRDP before 3.29.0 Heap Out-of-Bounds Read via GLYPH_FRAGMENT_ADD

## Summary
Severity: Medium
Advisory: CVE-2026-67291
Aliases: GHSA-hgj8-g595-wfc6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67291
Type: osv

## Details
FreeRDP before 3.29.0 (affected versions <= 3.28.0) contains a heap out-of-bounds read in update_process_glyph_fragments()/glyph_cache_fragment_put() in libfreerdp/cache/glyph.c. When handling a GLYPH_FRAGMENT_ADD update, the code reads a one-byte server-controlled declared fragment size but does not verify it fits within the remaining received buffer before allocating and copying that many bytes. A malicious RDP server can send a short fragment with an oversized declared size, causing the client to read beyond the allocated buffer, resulting in an out-of-bounds read and client crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67291.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-hgj8-g595-wfc6
- https://nvd.nist.gov/vuln/detail/CVE-2026-67291
- https://www.vulncheck.com/advisories/freerdp-before-heap-out-of-bounds-read-via-glyph-fragment-add
- https://github.com/FreeRDP/FreeRDP/commit/f3b4347105114fe7453828736bea069999af319f
