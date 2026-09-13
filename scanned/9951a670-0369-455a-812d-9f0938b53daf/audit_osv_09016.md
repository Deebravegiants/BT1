# [H] CVE-2016-7418

## Summary
Severity: High
Advisory: CVE-2016-7418
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/CVE-2016-7418
Type: osv

## Details
The php_wddx_push_element function in ext/wddx/wddx.c in PHP before 5.6.26 and 7.x before 7.0.11 allows remote attackers to cause a denial of service (invalid pointer access and out-of-bounds read) or possibly have unspecified other impact via an incorrect boolean element in a wddxPacket XML document, leading to mishandling in a wddx_deserialize call.

## References
- http://www.securityfocus.com/bid/93011
- http://www.securitytracker.com/id/1036836
- https://www.tenable.com/security/tns-2016-19
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://access.redhat.com/errata/RHSA-2018:1296
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=73065
- https://github.com/php/php-src/commit/c4cca4c20e75359c9a13a1f9a36cb7b4e9601d29?w=1
- http://www.openwall.com/lists/oss-security/2016/09/15/10
