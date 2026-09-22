# [C] CVE-2016-5114

## Summary
Severity: Critical
Advisory: CVE-2016-5114
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5114
Type: osv

## Details
sapi/fpm/fpm/fpm_log.c in PHP before 5.5.31, 5.6.x before 5.6.17, and 7.x before 7.0.2 misinterprets the semantics of the snprintf return value, which allows attackers to obtain sensitive information from process memory or cause a denial of service (out-of-bounds read and buffer overflow) via a long string, as demonstrated by a long URI in a configuration with custom REQUEST_URI logging.

## References
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.openwall.com/lists/oss-security/2016/05/29/1
- http://github.com/php/php-src/commit/2721a0148649e07ed74468f097a28899741eb58f?w=1
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://www.search-lab.hu/about-us/news/111-some-unusual-vulnerabilities-in-the-php-engine
- https://bugs.php.net/bug.php?id=70755
