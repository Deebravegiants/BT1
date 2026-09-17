# [C] CVE-2016-7129

## Summary
Severity: Critical
Advisory: CVE-2016-7129
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7129
Type: osv

## Details
The php_wddx_process_data function in ext/wddx/wddx.c in PHP before 5.6.25 and 7.x before 7.0.10 allows remote attackers to cause a denial of service (segmentation fault) or possibly have unspecified other impact via an invalid ISO 8601 time value, as demonstrated by a wddx_deserialize call that mishandles a dateTime element in a wddxPacket XML document.

## References
- http://www.securityfocus.com/bid/92758
- http://www.securitytracker.com/id/1036680
- https://www.tenable.com/security/tns-2016-19
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72749
- https://github.com/php/php-src/commit/426aeb2808955ee3d3f52e0cfb102834cdb836a5?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
