# [M] CVE-2018-14394

## Summary
Severity: Medium
Advisory: CVE-2018-14394
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14394
Type: osv

## Details
libavformat/movenc.c in FFmpeg before 4.0.2 allows attackers to cause a denial of service (application crash caused by a divide-by-zero error) with a user crafted Waveform audio file.

## References
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- https://github.com/FFmpeg/FFmpeg/commit/3a2d21bc5f97aa0161db3ae731fc2732be6108b8
