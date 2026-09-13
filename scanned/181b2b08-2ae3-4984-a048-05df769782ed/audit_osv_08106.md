# [H] CVE-2016-10268

## Summary
Severity: High
Advisory: CVE-2016-10268
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10268
Type: osv

## Details
tools/tiffcp.c in LibTIFF 4.0.7 allows remote attackers to cause a denial of service (integer underflow and heap-based buffer under-read) or possibly have unspecified other impact via a crafted TIFF image, related to "READ of size 78490" and libtiff/tif_unix.c:115:23.

## References
- http://www.securityfocus.com/bid/97202
- https://usn.ubuntu.com/3602-1/
- https://security.gentoo.org/glsa/201709-27
- https://blogs.gentoo.org/ago/2017/01/01/libtiff-multiple-heap-based-buffer-overflow/
- https://github.com/vadz/libtiff/commit/5397a417e61258c69209904e652a1f409ec3b9df
