# [M] CVE-2017-14056

## Summary
Severity: Medium
Advisory: CVE-2017-14056
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14056
Type: osv

## Details
In libavformat/rl2.c in FFmpeg 3.3.3, a DoS in rl2_read_header() due to lack of an EOF (End of File) check might cause huge CPU and memory consumption. When a crafted RL2 file, which claims a large "frame_count" field in the header but does not contain sufficient backing data, is provided, the loops (for offset and size tables) would consume huge CPU and memory resources, since there is no EOF check inside these loops.

## References
- http://www.securityfocus.com/bid/100628
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/96f24d1bee7fe7bac08e2b7c74db1a046c9dc0de
