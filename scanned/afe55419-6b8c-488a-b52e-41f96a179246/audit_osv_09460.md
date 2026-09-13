# [C] CVE-2016-9936

## Summary
Severity: Critical
Advisory: CVE-2016-9936
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-9936
Type: osv

## Details
The unserialize implementation in ext/standard/var.c in PHP 7.x before 7.0.14 allows remote attackers to cause a denial of service (use-after-free) or possibly have unspecified other impact via crafted serialized data.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-6834.

## References
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00034.html
- http://www.securityfocus.com/bid/94849
- https://access.redhat.com/errata/RHSA-2018:1296
- https://bugs.php.net/bug.php?id=72978
- http://www.php.net/ChangeLog-7.php
- https://github.com/php/php-src/commit/b2af4e8868726a040234de113436c6e4f6372d17
- http://www.openwall.com/lists/oss-security/2016/12/12/2
