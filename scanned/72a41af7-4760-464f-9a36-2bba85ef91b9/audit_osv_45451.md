# [C] FFmpeg through 8.1.2, fixed in commit 5d7112c, contains a heap out-of-bounds write vulnerability...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1182
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1182
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg through 8.1.2, fixed in commit 5d7112c, contains a heap out-of-bounds write vulnerability in the `vf_hqdn3d` filter that allows attackers to corrupt heap memory by supplying a crafted video whose frame resolution increases between frames when filtergraph reinitialization is disabled via the -reinit_filter 0 option. Attackers can provide a malicious video input where `vf_hqdn3d.config_input()` allocates undersized per-plane line-history buffers based on the initial frame width, and subsequent larger frames cause `denoise_spatial()` to write beyond the allocation boundary, resulting in heap memory corruption.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/5d7112c60e6f0f0742ce47d448e6da0718a70f4c
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23783
- https://github.com/advisories/GHSA-575m-jfmw-q76c
- https://nvd.nist.gov/vuln/detail/CVE-2026-66036
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-in-vf-hqdn3d-filter
