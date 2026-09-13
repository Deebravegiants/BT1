# [C] FFmpeg through 8.1.2, fixed in commit aafb5c6, contains a signed integer overflow vulnerability...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1185
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1185
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg through 8.1.2, fixed in commit aafb5c6, contains a signed integer overflow vulnerability in the MACE6 audio decoder that allows attackers to corrupt heap memory by supplying a crafted CAF file with a malicious `bytes_per_packet` value. Attackers can craft a CAF file with oversized `bytes_per_packet` and `frames_per_packet` values in the desc chunk to trigger an integer overflow in `mace_decode_frame()` during output sample count computation, resulting in an undersized buffer allocation and heap out-of-bounds write that could enable code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/aafb5c655edc76a753275c383ebb139feb032718
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23631
- https://github.com/advisories/GHSA-84qc-6h9r-4w33
- https://nvd.nist.gov/vuln/detail/CVE-2026-66039
- https://www.vulncheck.com/advisories/ffmpeg-mace6-audio-decoder-heap-out-of-bounds-write-via-caf-file
