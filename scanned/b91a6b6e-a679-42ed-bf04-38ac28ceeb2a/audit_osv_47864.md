# [M] CVE-2017-14042

## Summary
Severity: Medium
Advisory: CVE-2017-14042
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-14042
Type: osv

## Details
A memory allocation failure was discovered in the ReadPNMImage function in coders/pnm.c in GraphicsMagick 1.3.26. The vulnerability causes a big memory allocation, which may lead to remote denial of service in the MagickRealloc function in magick/memory.c.

## References
- https://usn.ubuntu.com/4206-1/
- http://www.securityfocus.com/bid/100556
- http://hg.code.sf.net/p/graphicsmagick/code/rev/3bbf7a13643d
- https://blogs.gentoo.org/ago/2017/08/28/graphicsmagick-memory-allocation-failure-in-magickrealloc-memory-c-2/
