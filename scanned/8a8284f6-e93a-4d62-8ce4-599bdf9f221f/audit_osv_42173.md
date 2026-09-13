# [C] FFmpeg 2.1 - 8.1.2 Heap Buffer Overflow via VobSub Subtitle Demuxer

## Summary
Severity: Critical
Advisory: CVE-2026-64830
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-64830
Type: osv

## Details
FFmpeg versions 2.1 through 8.1.2 contains a heap buffer overflow vulnerability in the VobSub subtitle demuxer that allows attackers to corrupt adjacent heap memory by supplying a malicious .sub/.idx subtitle file declaring more distinct stream IDs than the fixed-size array bounds in libavformat/mpeg.c. Attackers can craft a subtitle file with excessive distinct stream IDs to trigger unbounded writes beyond the vobsub->q[] array boundary via ff_subtitles_queue_insert(), potentially achieving arbitrary code execution in any application using FFmpeg's VobSub demuxer.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64830.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64830
- https://www.vulncheck.com/advisories/ffmpeg-heap-buffer-overflow-via-vobsub-subtitle-demuxer
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23657
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/dbd495f066a85ba96b17433f4306582aa37c3951
