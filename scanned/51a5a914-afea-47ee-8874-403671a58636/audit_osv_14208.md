# [H] CVE-2018-7998

## Summary
Severity: High
Advisory: CVE-2018-7998
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-7998
Type: osv

## Details
In libvips before 8.6.3, a NULL function pointer dereference vulnerability was found in the vips_region_generate function in region.c, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted image file. This occurs because of a race condition involving a failed delayed load and other worker threads.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00009.html
- https://github.com/jcupitt/libvips/commit/20d840e6da15c1574b3ed998bc92f91d1e36c2a5
- https://github.com/jcupitt/libvips/issues/893
