# [H] FreeRDP: H.264 YUV Buffer Dimension Desync - Heap OOB Write

## Summary
Severity: High
Advisory: CVE-2026-33986
Aliases: GHSA-h6qw-wxvm-hf97
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33986
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, in yuv_ensure_buffer() in libfreerdp/codec/h264.c, h264->width and h264->height are updated before the reallocation loop. If any winpr_aligned_recalloc() call fails, the function returns FALSE but width/height are already inflated. This issue has been patched in version 3.24.2.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33986.json
- https://access.redhat.com/security/cve/CVE-2026-33986
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33986.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-h6qw-wxvm-hf97
- https://nvd.nist.gov/vuln/detail/CVE-2026-33986
- https://bugzilla.redhat.com/show_bug.cgi?id=2453221
- https://github.com/FreeRDP/FreeRDP/commit/f6e43e208958140074ae9bb93cd0c9045a371c77
