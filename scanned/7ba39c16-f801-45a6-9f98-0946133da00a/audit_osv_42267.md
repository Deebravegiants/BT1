# [C] FFmpeg Heap Out-of-Bounds Write in vf_hqdn3d Filter

## Summary
Severity: Critical
Advisory: CVE-2026-66036
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66036
Type: osv

## Details
FFmpeg through 8.1.2, fixed in commit 5d7112c, contains a heap out-of-bounds write vulnerability in the vf_hqdn3d filter that allows attackers to corrupt heap memory by supplying a crafted video whose frame resolution increases between frames when filtergraph reinitialization is disabled via the -reinit_filter 0 option. Attackers can provide a malicious video input where vf_hqdn3d.config_input() allocates undersized per-plane line-history buffers based on the initial frame width, and subsequent larger frames cause denoise_spatial() to write beyond the allocation boundary, resulting in heap memory corruption.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66036.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66036
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-in-vf-hqdn3d-filter
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23783
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/5d7112c60e6f0f0742ce47d448e6da0718a70f4c
