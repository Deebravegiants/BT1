# [C] CVE-2016-7568

## Summary
Severity: Critical
Advisory: CVE-2016-7568
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-28
Source: https://osv.dev/vulnerability/CVE-2016-7568
Type: osv

## Details
Integer overflow in the gdImageWebpCtx function in gd_webp.c in the GD Graphics Library (aka libgd) through 2.2.3, as used in PHP through 7.0.11, allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via crafted imagewebp and imagedestroy calls.

## References
- http://www.debian.org/security/2016/dsa-3693
- http://www.securityfocus.com/bid/93184
- https://security.gentoo.org/glsa/201612-09
- https://bugs.php.net/bug.php?id=73003
- https://github.com/libgd/libgd/commit/40bec0f38f50e8510f5bb71a82f516d46facde03
- https://github.com/libgd/libgd/issues/308
- https://github.com/php/php-src/commit/c18263e0e0769faee96a5d0ee04b750c442783c6
