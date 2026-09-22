# [H] CVE-2017-11102

## Summary
Severity: High
Advisory: CVE-2017-11102
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/CVE-2017-11102
Type: osv

## Details
The ReadOneJNGImage function in coders/png.c in GraphicsMagick 1.3.26 allows remote attackers to cause a denial of service (application crash) during JNG reading via a zero-length color_image data structure.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00002.html
- https://usn.ubuntu.com/4206-1/
- https://www.debian.org/security/2018/dsa-4321
- http://www.securityfocus.com/bid/99498
- http://hg.code.sf.net/p/graphicsmagick/code/rev/d445af60a8d5
- http://hg.code.sf.net/p/graphicsmagick/code/rev/dea93a690fc1
