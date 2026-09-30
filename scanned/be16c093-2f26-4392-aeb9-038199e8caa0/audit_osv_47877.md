# [M] CVE-2017-14165

## Summary
Severity: Medium
Advisory: CVE-2017-14165
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-06
Source: https://osv.dev/vulnerability/CVE-2017-14165
Type: osv

## Details
The ReadSUNImage function in coders/sun.c in GraphicsMagick 1.3.26 has an issue where memory allocation is excessive because it depends only on a length field in a header. This may lead to remote denial of service in the MagickMalloc function in magick/memory.c.

## References
- https://usn.ubuntu.com/4232-1/
- http://www.securityfocus.com/bid/100678
- https://blogs.gentoo.org/ago/2017/09/06/graphicsmagick-memory-allocation-failure-in-magickmalloc-memory-c-2/
- http://hg.code.sf.net/p/graphicsmagick/code/rev/493da54370aa
