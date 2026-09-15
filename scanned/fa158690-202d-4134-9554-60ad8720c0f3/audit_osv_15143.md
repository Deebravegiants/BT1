# [C] CVE-2019-13962

## Summary
Severity: Critical
Advisory: CVE-2019-13962
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-13962
Type: osv

## Details
lavc_CopyPicture in modules/codec/avcodec/video.c in VideoLAN VLC media player through 3.0.7 has a heap-based buffer over-read because it does not properly validate the width and height.

## References
- http://git.videolan.org/?p=vlc/vlc-3.0.git%3Ba=commit%3Bh=2b4f9d0b0e0861f262c90e9b9b94e7d53b864509
- http://www.securityfocus.com/bid/109306
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00081.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00046.html
- https://seclists.org/bugtraq/2019/Aug/36
- https://security.gentoo.org/glsa/201909-02
- https://usn.ubuntu.com/4131-1/
- https://www.debian.org/security/2019/dsa-4504
- https://trac.videolan.org/vlc/ticket/22240
