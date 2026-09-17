# [C] CVE-2016-5768

## Summary
Severity: Critical
Advisory: CVE-2016-5768
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5768
Type: osv

## Details
Double free vulnerability in the _php_mb_regex_ereg_replace_exec function in php_mbregex.c in the mbstring extension in PHP before 5.5.37, 5.6.x before 5.6.23, and 7.x before 7.0.8 allows remote attackers to execute arbitrary code or cause a denial of service (application crash) by leveraging a callback exception.

## References
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00004.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00003.html
- http://www.securityfocus.com/bid/91396
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://support.apple.com/HT207170
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2598.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3618
- http://www.openwall.com/lists/oss-security/2016/06/23/4
- http://github.com/php/php-src/commit/5b597a2e5b28e2d5a52fc1be13f425f08f47cb62?w=1
- http://php.net/ChangeLog-5.php
- https://bugs.php.net/bug.php?id=72402
