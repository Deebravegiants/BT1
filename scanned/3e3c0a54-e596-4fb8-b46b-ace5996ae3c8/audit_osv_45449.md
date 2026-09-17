# [C] FFmpeg versions 3.4 through 8.1.2 contain an out-of-bounds write vulnerability in the...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1180
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1180
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg versions 3.4 through 8.1.2 contain an out-of-bounds write vulnerability in the `vf_floodfill` video filter that allows attackers to corrupt heap memory by supplying a dynamically sized video stream with filtergraph reinitialization disabled via -reinit_filter 0. When `config_input()` allocates the points traversal stack based on initial frame dimensions and a subsequent larger frame is processed, `filter_frame()` performs flood-fill neighbor pushes beyond the original allocation boundary, resulting in heap corruption and process crash with potential for code execution depending on heap layout and process hardening.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/f186c50cf53aec20e9a29059cb22ca3f2d59201c
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23780
- https://github.com/advisories/GHSA-gf7r-r5xq-r3hm
- https://nvd.nist.gov/vuln/detail/CVE-2026-65705
- https://www.vulncheck.com/advisories/ffmpeg-vf-floodfill-out-of-bounds-write-via-filter-frame
