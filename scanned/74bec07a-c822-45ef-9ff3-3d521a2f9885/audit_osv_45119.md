# [M] In FFmpeg 3.2 and 4.1, a denial of service in the subtitle decoder allows attackers to hog the CPU...

## Summary
Severity: Medium
Advisory: JLSEC-2025-102
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-102
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <4.3.1+0

## Details
In FFmpeg 3.2 and 4.1, a denial of service in the subtitle decoder allows attackers to hog the CPU via a crafted video file in Matroska format, because `ff_htmlmarkup_to_ass` in `libavcodec/htmlsubtitles.c` has a complex format argument to sscanf.

## References
- http://www.securityfocus.com/bid/107382
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/1f00c97bc3475c477f3c468cf2d924d5761d0982
- https://github.com/FFmpeg/FFmpeg/commit/23ccf3cabb4baf6e8af4b1af3fcc59c904736f21
- https://seclists.org/bugtraq/2019/May/60
- https://usn.ubuntu.com/3967-1/
- https://www.debian.org/security/2019/dsa-4449
