# [H] CVE-2019-14535

## Summary
Severity: High
Advisory: CVE-2019-14535
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-14535
Type: osv

## Details
A divide-by-zero error exists in the SeekIndex function of demux/asf/asf.c in VideoLAN VLC media player 3.0.7.1. As a result, an FPE can be triggered via a crafted WMV file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00046.html
- https://usn.ubuntu.com/4131-1/
- https://seclists.org/bugtraq/2019/Aug/36
- https://security.gentoo.org/glsa/201909-02
- https://www.debian.org/security/2019/dsa-4504
- http://git.videolan.org/?p=vlc.git&a=search&h=refs/heads/master&st=commit&s=cve-2019
- https://www.videolan.org/security/sb-vlc308.html
