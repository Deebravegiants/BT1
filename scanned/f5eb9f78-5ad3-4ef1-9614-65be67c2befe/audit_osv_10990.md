# [H] CVE-2017-5563

## Summary
Severity: High
Advisory: CVE-2017-5563
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-23
Source: https://osv.dev/vulnerability/CVE-2017-5563
Type: osv

## Details
LibTIFF version 4.0.7 is vulnerable to a heap-based buffer over-read in tif_lzw.c resulting in DoS or code execution via a crafted bmp image to tools/bmp2tiff.

## References
- https://usn.ubuntu.com/3606-1/
- http://www.securityfocus.com/bid/95705
- https://security.gentoo.org/glsa/201709-27
- http://bugzilla.maptools.org/show_bug.cgi?id=2664
