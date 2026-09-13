# [C] FFmpeg 4.4 - 8.1.2 Out-of-Bounds Memory Access in ADX Audio Decoder

## Summary
Severity: Critical
Advisory: CVE-2026-64835
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-64835
Type: osv

## Details
FFmpeg versions 4.4 through 8.1.2 contain an out-of-bounds memory access vulnerability in the ADX audio decoder within libavcodec/adxdec.c that allows attackers to trigger both out-of-bounds reads and writes by supplying a crafted ADX or AAX audio file with a mid-stream channel layout change. When AV_PKT_DATA_NEW_EXTRADATA side data is received mid-stream, the adx_decode_frame function re-parses the stream header but fails to update the internal channel state, causing subsequent decoding operations to access the prev[] state array using a stale channel count.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64835.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64835
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-memory-access-in-adx-audio-decoder
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23659
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/1836ef96846937a6cc2443698a693104f5c0b21e
