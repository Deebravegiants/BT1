# [H] CVE-2016-2330

## Summary
Severity: High
Advisory: CVE-2016-2330
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/CVE-2016-2330
Type: osv

## Details
libavcodec/gif.c in FFmpeg before 2.8.6 does not properly calculate a buffer size, which allows remote attackers to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact via a crafted .tga file, related to the gif_image_write_image, gif_encode_init, and gif_encode_close functions.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=03d83ba34b2070878909eae18dfac0f519503777
- http://www.securityfocus.com/bid/84217
- http://www.securitytracker.com/id/1035010
- http://www.ubuntu.com/usn/USN-2944-1
- https://security.gentoo.org/glsa/201606-09
