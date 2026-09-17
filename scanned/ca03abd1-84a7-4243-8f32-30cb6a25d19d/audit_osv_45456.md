# [C] FFmpeg 7.0 through 8.1.2, fixed in commit 4da9812, contains a heap out-of-bounds write...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1187
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1187
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=7.1.0+0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=7.1.0+0 <9.0.0+0

## Details
FFmpeg 7.0 through 8.1.2, fixed in commit 4da9812, contains a heap out-of-bounds write vulnerability in the `vf_quirc` filter that allows an attacker to corrupt heap memory by supplying a crafted PGS/SUP subtitle file with mismatched frame dimensions. Attackers can provide a subtitle file whose second presentation has larger dimensions than its first, causing `av_image_copy_plane()` to copy data exceeding the initial allocation size into the undersized libquirc grayscale image buffer, resulting in heap corruption and process crash with potential for code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/4da9812e25894fb51d62a8875cfa8eb39b5e20f5
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23625
- https://github.com/advisories/GHSA-frhp-m687-9g3q
- https://nvd.nist.gov/vuln/detail/CVE-2026-66041
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-via-vf-quirc-filter
