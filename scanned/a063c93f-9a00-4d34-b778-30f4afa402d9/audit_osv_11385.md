# [H] CVE-2017-7597

## Summary
Severity: High
Advisory: CVE-2017-7597
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7597
Type: osv

## Details
tif_dirread.c in LibTIFF 4.0.7 has an "outside the range of representable values of type float" undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image.

## References
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/97504
- https://security.gentoo.org/glsa/201709-27
- https://blogs.gentoo.org/ago/2017/04/01/libtiff-multiple-ubsan-crashes
