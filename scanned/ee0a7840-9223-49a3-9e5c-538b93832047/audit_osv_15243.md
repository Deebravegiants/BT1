# [H] CVE-2019-14778

## Summary
Severity: High
Advisory: CVE-2019-14778
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-14778
Type: osv

## Details
The mkv::virtual_segment_c::seek method of demux/mkv/virtual_segment.cpp in VideoLAN VLC media player 3.0.7.1 has a use-after-free.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00046.html
- https://usn.ubuntu.com/4131-1/
- https://seclists.org/bugtraq/2019/Aug/36
- https://security.gentoo.org/glsa/201909-02
- https://www.debian.org/security/2019/dsa-4504
- http://git.videolan.org/?p=vlc.git&a=search&h=refs/heads/master&st=commit&s=cve-2019
- https://www.videolan.org/security/sb-vlc308.html
