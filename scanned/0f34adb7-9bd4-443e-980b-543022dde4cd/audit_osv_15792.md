# [H] CVE-2019-19721

## Summary
Severity: High
Advisory: CVE-2019-19721
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-15
Source: https://osv.dev/vulnerability/CVE-2019-19721
Type: osv

## Details
An off-by-one error in the DecodeBlock function in codec/sdl_image.c in VideoLAN VLC media player before 3.0.9 allows remote attackers to cause a denial of service (memory corruption) via a crafted image file. NOTE: this may be related to the SDL_Image product.

## References
- https://git.videolan.org/?p=vlc/vlc-3.0.git%3Ba=commit%3Bh=72afe7ebd8305bf4f5360293b8621cde52ec506b
- http://hg.libsdl.org/SDL_image/
- https://www.videolan.org/security/
- https://bugs.gentoo.org/721940
