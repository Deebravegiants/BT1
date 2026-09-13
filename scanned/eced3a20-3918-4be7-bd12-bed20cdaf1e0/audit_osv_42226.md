# [C] FFmpeg 8.1.2 Out-of-Bounds Write via TY Demuxer and Shorten Decoder

## Summary
Severity: Critical
Advisory: CVE-2026-65704
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65704
Type: osv

## Details
FFmpeg through 8.1.2 contains an out-of-bounds write vulnerability that allows attackers to cause heap corruption by supplying a crafted ffconcat file processed with the -safe 0 flag. The TY demuxer's demux_audio() function decrements packet size without bounds checking, producing a negative size value that is passed to memcpy() in shorten_decode_frame(), where conversion to size_t wraps the value to near SIZE_MAX and triggers reads beyond the source allocation and writes far beyond the Shorten decoder's bitstream buffer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65704.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65704
- https://www.vulncheck.com/advisories/ffmpeg-out-of-bounds-write-via-ty-demuxer-and-shorten-decoder
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23767
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/de771bd52774a52d45b0e2c82e56995a1ef40df7
