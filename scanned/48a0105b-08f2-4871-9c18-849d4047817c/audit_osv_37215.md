# [M] FreeRDP has a heap-buffer-overflow in bitmap_cache_put via OOB cacheId

## Summary
Severity: Medium
Advisory: CVE-2026-29775
Aliases: GHSA-h666-rfw3-jhvj
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-29775
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.24.0, a client-side heap out-of-bounds read/write occurs in FreeRDP's bitmap cache subsystem due to an off-by-one boundary check in bitmap_cache_put. A malicious server can send a CACHE_BITMAP_ORDER (Rev1) with cacheId equal to maxCells, bypassing the guard and accessing cells[] one element past the allocated array. This vulnerability is fixed in 3.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29775.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-h666-rfw3-jhvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-29775
- https://github.com/FreeRDP/FreeRDP/commit/ffad58fd2b329efd81a3239e9d7e3c927b8e503f
