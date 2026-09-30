# [H] CVE-2016-5093

## Summary
Severity: High
Advisory: CVE-2016-5093
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5093
Type: osv

## Details
The get_icu_value_internal function in ext/intl/locale/locale_methods.c in PHP before 5.5.36, 5.6.x before 5.6.22, and 7.x before 7.0.7 does not ensure the presence of a '\0' character, which allows remote attackers to cause a denial of service (out-of-bounds read) or possibly have unspecified other impact via a crafted locale_get_primary_language call.

## References
- http://www.securityfocus.com/bid/90946
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3602
- http://www.openwall.com/lists/oss-security/2016/05/26/3
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://github.com/php/php-src/commit/97eff7eb57fc2320c267a949cffd622c38712484?w=1
- https://bugs.php.net/bug.php?id=72241
