# [M] CVE-2019-14534

## Summary
Severity: Medium
Advisory: CVE-2019-14534
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-14534
Type: osv

## Details
In VideoLAN VLC media player 3.0.7.1, there is a NULL pointer dereference at the function SeekPercent of demux/asf/asf.c that will lead to a denial of service attack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00046.html
- https://usn.ubuntu.com/4131-1/
- https://seclists.org/bugtraq/2019/Aug/36
- https://security.gentoo.org/glsa/201909-02
- https://www.debian.org/security/2019/dsa-4504
- http://git.videolan.org/?p=vlc.git&a=search&h=refs/heads/master&st=commit&s=cve-2019
- https://www.videolan.org/security/sb-vlc308.html
