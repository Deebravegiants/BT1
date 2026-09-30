# [C] FreeRDP: Heap-buffer-overflow write in AVC444 YUV buffer allocation

## Summary
Severity: Critical
Advisory: CVE-2026-55191
Aliases: GHSA-vx73-w5q6-7jqr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55191
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.0, FreeRDP clients that negotiate RDPGFX AVC444 with an H.264 decoder backend calculate the intermediate YUV444 allocation size in libfreerdp/codec/h264.c with 32-bit multiplication in avc444_ensure_buffer. A malicious RDP server can supply surface dimensions for which piDstStride multiplied by padDstHeight wraps to a small nonzero value, causing winpr_aligned_recalloc to allocate an undersized buffer before YUV420CombineToYUV444 writes using the actual stride and rectangle dimensions. This can cause a client crash and may permit code execution through attacker-influenced heap corruption. This issue is fixed in version 3.27.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55191.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-vx73-w5q6-7jqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-55191
- https://github.com/FreeRDP/FreeRDP/commit/97f40b9e766af375f4e41ac6a3f4397d708d249c
- https://github.com/FreeRDP/FreeRDP/pull/12873
