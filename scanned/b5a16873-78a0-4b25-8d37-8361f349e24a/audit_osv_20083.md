# [H] CVE-2021-30123

## Summary
Severity: High
Advisory: CVE-2021-30123
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2021-30123
Type: osv

## Details
FFmpeg <=4.3 contains a buffer overflow vulnerability in libavcodec through a crafted file that may lead to remote code execution.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=d6f293353c94c7ce200f6e0975ae3de49787f91f
- https://security.gentoo.org/glsa/202105-24
- https://trac.ffmpeg.org/ticket/8845
- https://trac.ffmpeg.org/ticket/8863
