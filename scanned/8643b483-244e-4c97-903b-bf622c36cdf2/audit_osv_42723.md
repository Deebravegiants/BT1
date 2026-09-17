# [C] FFmpeg 4.4 < 9.0 Heap Out-of-Bounds Write in CFHD Decoder via AVI Demuxing

## Summary
Severity: Critical
Advisory: CVE-2026-70632
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70632
Type: osv

## Details
FFmpeg versions from 4.4 up to, but not including, 9.0 contain an out-of-bounds heap write vulnerability in the native GoPro CineForm HD (CFHD) decoder that allows remote attackers to corrupt heap memory by supplying a crafted AVI file during stream probing. The cfhd_decode() function fails to enforce the non-Bayer logical output-width invariant in the transform-type-2 reconstruction path, causing horiz_filter_clip() to write oversized 16-bit sample rows far beyond the allocated output frame buffer, which can be escalated to arbitrary code execution via overwrite of a live cleanup callback pointer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/1006a2151236f9235bf02822f263b3fb0532111e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70632.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70632
- https://www.vulncheck.com/advisories/ffmpeg-heap-out-of-bounds-write-in-cfhd-decoder-via-avi-demuxing
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23898
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/16b2049d4d5222db6cd7c031409058571c94f6a9
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/db05df9d135fb56a4babb836d5e9f5c1d984e087
