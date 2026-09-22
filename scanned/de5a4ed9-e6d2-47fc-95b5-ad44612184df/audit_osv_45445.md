# [M] FFmpeg versions 0.7.1 through 8.1.2 contain an out-of-bounds read vulnerability in the S/PDIF...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1175
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1175
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg versions 0.7.1 through 8.1.2 contain an out-of-bounds read vulnerability in the S/PDIF muxer that allows attackers to access memory beyond buffer boundaries by supplying a crafted DTS stream with a `core_size` value larger than the actual packet length. Attackers can exploit the missing bounds check in the `spdif_header_dts4` function by providing a malicious DTS-HD audio stream during S/PDIF re-muxing to trigger unauthorized memory reads beyond the packet buffer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/6f80e2765492700622596af720534cef33dd31b4
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23661
- https://github.com/advisories/GHSA-34g6-m4cp-w5c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-64833
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-read-via-s-pdif-muxer-spdifenc-c
