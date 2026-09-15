# [M] CVE-2017-14060

## Summary
Severity: Medium
Advisory: CVE-2017-14060
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14060
Type: osv

## Details
In ImageMagick 7.0.6-10, a NULL Pointer Dereference issue is present in the ReadCUTImage function in coders/cut.c that could allow an attacker to cause a Denial of Service (in the QueueAuthenticPixelCacheNexus function within the MagickCore/cache.c file) by submitting a malformed image file.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00007.html
- https://security.gentoo.org/glsa/201711-07
- https://usn.ubuntu.com/3681-1/
- https://github.com/ImageMagick/ImageMagick/issues/710
