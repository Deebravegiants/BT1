# [H] CVE-2017-7598

## Summary
Severity: High
Advisory: CVE-2017-7598
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7598
Type: osv

## Details
tif_dirread.c in LibTIFF 4.0.7 might allow remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted image.

## References
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/97499
- https://security.gentoo.org/glsa/201709-27
- https://blogs.gentoo.org/ago/2017/04/01/libtiff-multiple-ubsan-crashes
