# [M] CVE-2017-13131

## Summary
Severity: Medium
Advisory: CVE-2017-13131
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-23
Source: https://osv.dev/vulnerability/CVE-2017-13131
Type: osv

## Details
In ImageMagick 7.0.6-8, a memory leak vulnerability was found in the function ReadMIFFImage in coders/miff.c, which allows attackers to cause a denial of service (memory consumption in NewLinkedList in MagickCore/linked-list.c) via a crafted file.

## References
- http://www.securityfocus.com/bid/100478
- https://usn.ubuntu.com/3681-1/
- https://security.gentoo.org/glsa/201711-07
- https://github.com/ImageMagick/ImageMagick/issues/676
