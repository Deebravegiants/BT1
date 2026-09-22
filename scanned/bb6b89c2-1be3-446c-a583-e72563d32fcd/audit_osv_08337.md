# [H] CVE-2016-2328

## Summary
Severity: High
Advisory: CVE-2016-2328
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/CVE-2016-2328
Type: osv

## Details
libswscale/swscale_unscaled.c in FFmpeg before 2.8.6 does not validate certain height values, which allows remote attackers to cause a denial of service (out-of-bounds array read access) or possibly have unspecified other impact via a crafted .cine file, related to the bayer_to_rgb24_wrapper and bayer_to_yv12_wrapper functions.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=757248ea3cd917a7755cb15f817a9b1f15578718
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=ad3b6fa7d83db7de951ed891649af93a47e74be5
- http://www.securitytracker.com/id/1035010
- https://security.gentoo.org/glsa/201606-09
