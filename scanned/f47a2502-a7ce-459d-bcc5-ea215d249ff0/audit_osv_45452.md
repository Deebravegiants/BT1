# [M] FFmpeg through 8.1.2, fixed in commit 5d7112c, contains an uncontrolled resource consumption...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1183
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1183
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg through 8.1.2, fixed in commit 5d7112c, contains an uncontrolled resource consumption vulnerability in the IAMF demuxer that allows an unauthenticated attacker to cause multi-gigabyte memory allocation from a 17-byte input file by supplying a crafted `count_label` field. The `mix_presentation_obu()` function in `libavformat/iamf_parse.c` calls `av_calloc`(`count_label`, sizeof(*`language_label`)) with an attacker-controlled value before validating available OBU data, enabling an allocation amplification of approximately 126 million bytes per input byte that exhausts process memory or triggers an OOM-kill during format probing.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/86708357d126af84c16f80d9c57335d1e8c845c5
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23627
- https://github.com/advisories/GHSA-qqrg-chvw-q8jp
- https://nvd.nist.gov/vuln/detail/CVE-2026-66037
- https://www.vulncheck.com/advisories/ffmpeg-iamf-demuxer-uncontrolled-resource-consumption-via-mix-presentation-obu
