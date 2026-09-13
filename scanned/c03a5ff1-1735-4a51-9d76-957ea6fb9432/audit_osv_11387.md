# [H] CVE-2017-7599

## Summary
Severity: High
Advisory: CVE-2017-7599
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7599
Type: osv

## Details
LibTIFF 4.0.7 has an "outside the range of representable values of type short" undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image.

## References
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/97505
- http://www.securityfocus.com/bid/97508
- https://security.gentoo.org/glsa/201709-27
- https://blogs.gentoo.org/ago/2017/04/01/libtiff-multiple-ubsan-crashes
