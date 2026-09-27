# [H] FreeRDP: Persistent Cache bmpSize Desync - Heap OOB Write

## Summary
Severity: High
Advisory: CVE-2026-33987
Aliases: GHSA-ff8h-p5vc-wcwc
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33987
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, in persistent_cache_read_entry_v3() in libfreerdp/cache/persistent.c, persistent->bmpSize is updated before winpr_aligned_recalloc(). If realloc fails, bmpSize is inflated while bmpData points to the old buffer. This issue has been patched in version 3.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33987.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-ff8h-p5vc-wcwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33987
- https://github.com/FreeRDP/FreeRDP/commit/1a890eb43492b5eb707cb3dd6fc908f696e8fc1c
