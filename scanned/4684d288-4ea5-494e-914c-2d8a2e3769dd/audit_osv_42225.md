# [C] FFmpeg 2.7 - 8.1.2 Out-of-Bounds Write in TDSC Video Decoder

## Summary
Severity: Critical
Advisory: CVE-2026-65703
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65703
Type: osv

## Details
FFmpeg versions 2.7 through 8.1.2 contain an out-of-bounds write vulnerability in the TDSC video decoder that allows remote attackers to cause heap corruption by supplying a crafted AVI file that changes frame dimensions across TDSF frames. The tdsc_parse_tdsf() function fails to unreference the existing reference frame before calling av_frame_get_buffer(), causing tdsc_blit() and tdsc_yuv2rgb() to write attacker-controlled pixel data beyond the end of the undersized reference frame buffer, resulting in a process crash and potential code execution.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65703.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65703
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-write-in-tdsc-video-decoder
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23773
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/fd3ee52fab34d98a95b787d0b5ff45685766200c
