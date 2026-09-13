# [M] CVE-2018-6392

## Summary
Severity: Medium
Advisory: CVE-2018-6392
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-29
Source: https://osv.dev/vulnerability/CVE-2018-6392
Type: osv

## Details
The filter_slice function in libavfilter/vf_transpose.c in FFmpeg through 3.4.1 allows remote attackers to cause a denial of service (out-of-array access) via a crafted MP4 file.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00041.html
- http://www.securityfocus.com/bid/102848
- https://www.debian.org/security/2018/dsa-4249
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/3f621455d62e46745453568d915badd5b1e5bcd5
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/c6939f65a116b1ffed345d29d8621ee4ffb32235
