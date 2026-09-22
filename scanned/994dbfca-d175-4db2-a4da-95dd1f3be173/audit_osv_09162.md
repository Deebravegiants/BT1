# [C] CVE-2016-8670

## Summary
Severity: Critical
Advisory: CVE-2016-8670
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-8670
Type: osv

## Details
Integer signedness error in the dynamicGetbuf function in gd_io_dp.c in the GD Graphics Library (aka libgd) through 2.2.3, as used in PHP before 5.6.28 and 7.x before 7.0.13, allows remote attackers to cause a denial of service (stack-based buffer overflow) or possibly have unspecified other impact via a crafted imagecreatefromstring call.

## References
- http://www.securityfocus.com/bid/93594
- https://support.f5.com/csp/article/K21336065?utm_source=f5support&amp%3Butm_medium=RSS
- http://www.debian.org/security/2016/dsa-3693
- http://www.openwall.com/lists/oss-security/2016/10/15/1
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=73280
- https://github.com/libgd/libgd/commit/53110871935244816bbb9d131da0bccff734bfe9
