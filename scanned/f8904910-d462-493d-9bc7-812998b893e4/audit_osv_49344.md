# [H] CVE-2019-10650

## Summary
Severity: High
Advisory: CVE-2019-10650
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2019-03-30
Source: https://osv.dev/vulnerability/CVE-2019-10650
Type: osv

## Details
In ImageMagick 7.0.8-36 Q16, there is a heap-based buffer over-read in the function WriteTIFFImage of coders/tiff.c, which allows an attacker to cause a denial of service or information disclosure via a crafted image file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00010.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00015.html
- https://usn.ubuntu.com/4034-1/
- http://www.securityfocus.com/bid/107646
- https://seclists.org/bugtraq/2019/Apr/37
- https://www.debian.org/security/2019/dsa-4436
- https://github.com/ImageMagick/ImageMagick/issues/1532
