# [C] CVE-2017-10699

## Summary
Severity: Critical
Advisory: CVE-2017-10699
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-30
Source: https://osv.dev/vulnerability/CVE-2017-10699
Type: osv

## Details
avcodec 2.2.x, as used in VideoLAN VLC media player 2.2.7-x before 2017-06-29, allows out-of-bounds heap memory write due to calling memcpy() with a wrong size, leading to a denial of service (application crash) or possibly code execution.

## References
- http://www.securitytracker.com/id/1038816
- https://www.debian.org/security/2017/dsa-4045
- https://trac.videolan.org/vlc/ticket/18467
