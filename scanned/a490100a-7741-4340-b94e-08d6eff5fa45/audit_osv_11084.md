# [M] CVE-2017-5975

## Summary
Severity: Medium
Advisory: CVE-2017-5975
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-01
Source: https://osv.dev/vulnerability/CVE-2017-5975
Type: osv

## Details
Heap-based buffer overflow in the __zzip_get64 function in fetch.c in zziplib 0.13.62, 0.13.61, 0.13.60, 0.13.59, 0.13.58, 0.13.57, 0.13.56 allows remote attackers to cause a denial of service (crash) via a crafted ZIP file.

## References
- http://www.debian.org/security/2017/dsa-3878
- http://www.securityfocus.com/bid/96268
- http://www.openwall.com/lists/oss-security/2017/02/14/3
- https://blogs.gentoo.org/ago/2017/02/09/zziplib-heap-based-buffer-overflow-in-__zzip_get64-fetch-c/
