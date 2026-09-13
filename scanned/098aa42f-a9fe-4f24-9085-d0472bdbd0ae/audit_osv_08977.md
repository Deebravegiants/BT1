# [H] CVE-2016-7130

## Summary
Severity: High
Advisory: CVE-2016-7130
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7130
Type: osv

## Details
The php_wddx_pop_element function in ext/wddx/wddx.c in PHP before 5.6.25 and 7.x before 7.0.10 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) or possibly have unspecified other impact via an invalid base64 binary value, as demonstrated by a wddx_deserialize call that mishandles a binary element in a wddxPacket XML document.

## References
- http://www.securityfocus.com/bid/92764
- http://www.securitytracker.com/id/1036680
- https://www.tenable.com/security/tns-2016-19
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72750
- https://github.com/php/php-src/commit/698a691724c0a949295991e5df091ce16f899e02?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
