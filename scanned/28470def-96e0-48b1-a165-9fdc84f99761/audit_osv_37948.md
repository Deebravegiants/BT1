# [H] FreeRDP: Persistent Cache Allocator Mismatch - Heap OOB Read

## Summary
Severity: High
Advisory: CVE-2026-33982
Aliases: GHSA-8jm9-2925-g4v2
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33982
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, there is a heap-buffer-overflow READ vulnerability at 24 bytes before the allocation, in winpr_aligned_offset_recalloc(). This issue has been patched in version 3.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33982.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-8jm9-2925-g4v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33982
- https://github.com/FreeRDP/FreeRDP/commit/a48dbde2c8a5b8b70a9d1c045d969a71afd6284c
