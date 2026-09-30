# [H] CVE-2016-6920

## Summary
Severity: High
Advisory: CVE-2016-6920
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2016-6920
Type: osv

## Details
Heap-based buffer overflow in the decode_block function in libavcodec/exr.c in FFmpeg before 3.1.3 allows remote attackers to cause a denial of service (application crash) via vectors involving tile positions.

## References
- http://git.videolan.org/gitweb.cgi/ffmpeg.git/?a=commit%3Bh=79f52a0dbd484aad111e4bf4a4f7047c7ceb6137
- http://www.securityfocus.com/archive/1/539368/100/0/threaded
- http://www.securityfocus.com/bid/92790
- http://packetstormsecurity.com/files/138618/ffmpeg-3.1.2-Heap-Overflow.html
- http://www.securityfocus.com/bid/92664
- https://www.ffmpeg.org/security.html
