# [H] CVE-2020-13428

## Summary
Severity: High
Advisory: CVE-2020-13428
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-13428
Type: osv

## Details
A heap-based buffer overflow in the hxxx_AnnexB_to_xVC function in modules/packetizer/hxxx_nal.c in VideoLAN VLC media player before 3.0.11 for macOS/iOS allows remote attackers to cause a denial of service (application crash) or execute arbitrary code via a crafted H.264 Annex-B video (.avi for example) file.

## References
- http://git.videolan.org/?p=vlc/vlc-3.0.git%3Ba=commit%3Bh=d5c43c21c747ff30ed19fcca745dea3481c733e0
- https://github.com/videolan/vlc-3.0/releases/tag/3.0.11
- https://www.debian.org/security/2020/dsa-4704
- https://www.videolan.org/security/sb-vlc3011.html
- https://github.com/videolan/vlc/commits/master/modules/packetizer/hxxx_nal.c
