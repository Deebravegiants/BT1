# [M] CVE-2015-1208

## Summary
Severity: Medium
Advisory: CVE-2015-1208
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-01-09
Source: https://osv.dev/vulnerability/CVE-2015-1208
Type: osv

## Details
Integer underflow in the mov_read_default function in libavformat/mov.c in FFmpeg before 2.4.6 allows remote attackers to obtain sensitive information from heap and/or stack memory via a crafted MP4 file.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=3ebd76a9c57558e284e94da367dd23b435e6a6d0
- https://bugs.chromium.org/p/chromium/issues/detail?id=444546
- https://github.com/FFmpeg/FFmpeg/blob/n2.4.6/Changelog
