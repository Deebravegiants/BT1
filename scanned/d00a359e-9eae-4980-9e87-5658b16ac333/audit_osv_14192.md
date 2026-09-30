# [M] CVE-2018-7751

## Summary
Severity: Medium
Advisory: CVE-2018-7751
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2018-7751
Type: osv

## Details
The svg_probe function in libavformat/img2dec.c in FFmpeg through 3.4.2 allows remote attackers to cause a denial of service (Infinite Loop) via a crafted XML file.

## References
- http://www.securityfocus.com/bid/103956
- https://security.gentoo.org/glsa/202003-65
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/a6cba062051f345e8ebfdff34aba071ed73d923f
