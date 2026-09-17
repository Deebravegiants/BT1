# [C] FFmpeg through 8.1.2, fixed in commit b506faf, contains a heap out-of-bounds write vulnerability...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1186
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1186
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <9.0.0+0
- Julia: `FFMPEG_nogpl_jll` — affected >=0 <9.0.0+0
- Julia: `FFplay_jll` — affected >=0 <9.0.0+0

## Details
FFmpeg through 8.1.2, fixed in commit b506faf, contains a heap out-of-bounds write vulnerability in the native PNG and APNG encoders that allows remote attackers to corrupt heap memory by supplying a crafted PNG image with a malicious eXIf chunk. Attackers can craft an eXIf chunk where multiple IFD entries reference the same large value payload, causing canonical serialization to expand the output far beyond the undersized allocation estimated by `add_exif_profile_size()`, resulting in `png_write_chunk()` writing tens of thousands of bytes past the buffer boundary, leading to deterministic heap corruption, process crash, and potentially arbitrary code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/b506fafec9a19fcbc2be5271875fd4a63d6615bc
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23786
- https://github.com/advisories/GHSA-6vcg-882j-82v5
- https://nvd.nist.gov/vuln/detail/CVE-2026-66040
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-via-png-apng-exif-encoder
