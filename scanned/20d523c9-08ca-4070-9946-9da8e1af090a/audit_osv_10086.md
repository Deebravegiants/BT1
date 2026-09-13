# [M] CVE-2017-13144

## Summary
Severity: Medium
Advisory: CVE-2017-13144
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13144
Type: osv

## Details
In ImageMagick before 6.9.7-10, there is a crash (rather than a "width or height exceeds limit" error report) if the image dimensions are too large, as demonstrated by use of the mpc coder.

## References
- https://usn.ubuntu.com/3681-1/
- https://security.gentoo.org/glsa/201711-07
- https://www.debian.org/security/2017/dsa-4019
- https://www.debian.org/security/2017/dsa-4040
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=869728
- https://www.imagemagick.org/discourse-server/viewtopic.php?f=3&t=31438
