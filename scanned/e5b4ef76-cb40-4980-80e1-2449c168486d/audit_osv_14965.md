# [C] CVE-2019-12730

## Summary
Severity: Critical
Advisory: CVE-2019-12730
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-04
Source: https://osv.dev/vulnerability/CVE-2019-12730
Type: osv

## Details
aa_read_header in libavformat/aadec.c in FFmpeg before 3.2.14 and 4.x before 4.1.4 does not check for sscanf failure and consequently allows use of uninitialized variables.

## References
- http://www.securityfocus.com/bid/109317
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/9b4004c054964a49c7ba44583f4cee22486dd8f2
- https://git.ffmpeg.org/gitweb/ffmpeg.git/shortlog/n4.1.4
- https://seclists.org/bugtraq/2019/Aug/30
- https://usn.ubuntu.com/4431-1/
- https://github.com/FFmpeg/FFmpeg/compare/a97ea53...ba11e40
- https://security.gentoo.org/glsa/202003-65
- https://www.debian.org/security/2019/dsa-4502
- https://github.com/FFmpeg/FFmpeg/commit/ed188f6dcdf0935c939ed813cf8745d50742014b
