# [H] CVE-2019-14438

## Summary
Severity: High
Advisory: CVE-2019-14438
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-14438
Type: osv

## Details
A heap-based buffer over-read in xiph_PackHeaders() in modules/demux/xiph.h in VideoLAN VLC media player 3.0.7.1 allows remote attackers to trigger a heap-based buffer over-read via a crafted .ogg file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00046.html
- https://usn.ubuntu.com/4131-1/
- https://seclists.org/bugtraq/2019/Aug/36
- https://security.gentoo.org/glsa/201909-02
- https://www.debian.org/security/2019/dsa-4504
- http://git.videolan.org/?p=vlc.git&a=search&h=refs%2Fheads%2Fmaster&st=commit&s=cve-2019
- https://www.videolan.org/security/sb-vlc308.html
