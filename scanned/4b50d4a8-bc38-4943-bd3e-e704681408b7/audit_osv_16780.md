# [M] CVE-2019-9721

## Summary
Severity: Medium
Advisory: CVE-2019-9721
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-12
Source: https://osv.dev/vulnerability/CVE-2019-9721
Type: osv

## Details
A denial of service in the subtitle decoder in FFmpeg 3.2 and 4.1 allows attackers to hog the CPU via a crafted video file in Matroska format, because handle_open_brace in libavcodec/htmlsubtitles.c has a complex format argument to sscanf.

## References
- http://www.securityfocus.com/bid/107384
- https://usn.ubuntu.com/3967-1/
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/894995c41e0795c7a44f81adc4838dedc3932e65
- https://github.com/FFmpeg/FFmpeg/commit/273f2755ce8635d42da3cde0eeba15b2e7842774
