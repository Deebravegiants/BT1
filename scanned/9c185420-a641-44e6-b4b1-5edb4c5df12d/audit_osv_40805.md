# [M] FreeRDP: Out-of-bounds read in glyph_cache_get via crafted glyph fragments

## Summary
Severity: Medium
Advisory: CVE-2026-55564
Aliases: GHSA-6xmj-pr98-cx4c
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55564
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.0, the glyph_cache_get function in libfreerdp/cache/glyph.c checks whether index is greater than cache->number instead of greater than or equal to it. A malicious RDP server can use GLYPH_FRAGMENT_USE replay in update_process_glyph_fragments to make the default cache receive index 254 when cache->number is 254, reading one pointer beyond the entries array and dereferencing it as a glyph. This can crash the client and may disclose adjacent heap data. This issue is fixed in version 3.27.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55564.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-6xmj-pr98-cx4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-55564
- https://github.com/FreeRDP/FreeRDP/commit/c29324750e3cbcba8761f147b7a5235cc686930f
- https://github.com/FreeRDP/FreeRDP/pull/12885
