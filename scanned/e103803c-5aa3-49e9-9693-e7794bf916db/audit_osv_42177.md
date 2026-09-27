# [M] FFmpeg 0.6.3 - 8.1.2 Infinite Loop DoS via RTP/ASF Demuxer

## Summary
Severity: Medium
Advisory: CVE-2026-64834
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-64834
Type: osv

## Details
FFmpeg versions 0.6.3 through 8.1.2 contain an infinite loop vulnerability in the RTP/ASF demuxer within libavformat/rtpdec_asf.c that allows remote attackers to cause denial of service by sending a crafted RTP/ASF stream. The rtp_asf_fix_header function fails to validate a minimum chunksize when iterating over ASF objects, causing the loop pointer to never advance when a chunksize is smaller than the 24-byte minimum ASF object header size, resulting in CPU exhaustion that denies service to legitimate users.

## References
- https://code.ffmpeg.org/FFmpeg/FFmpeg
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64834.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64834
- https://www.vulncheck.com/advisories/ffmpeg-infinite-loop-dos-via-rtp-asf-demuxer
- https://code.ffmpeg.org/FFmpeg/FFmpeg/pulls/23663
- https://code.ffmpeg.org/FFmpeg/FFmpeg/commit/11d5f475be95d22d5f0692220cc772b116abc632
