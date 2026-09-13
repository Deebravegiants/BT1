# [H] CVE-2016-4070

## Summary
Severity: High
Advisory: CVE-2016-4070
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-20
Source: https://osv.dev/vulnerability/CVE-2016-4070
Type: osv

## Details
Integer overflow in the php_raw_url_encode function in ext/standard/url.c in PHP before 5.5.34, 5.6.x before 5.6.20, and 7.x before 7.0.5 allows remote attackers to cause a denial of service (application crash) via a long string to the rawurlencode function. NOTE: the vendor says "Not sure if this qualifies as security issue (probably not).

## References
- http://lists.apple.com/archives/security-announce/2016/May/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00056.html
- http://www.openwall.com/lists/oss-security/2016/04/24/1
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- http://www.securityfocus.com/bid/85801
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=95433e8e339dbb6b5d5541473c1661db6ba2c451
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05320149
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05390722
- https://support.apple.com/HT206567
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3560
- http://www.ubuntu.com/usn/USN-2952-1
- http://www.ubuntu.com/usn/USN-2952-2
- https://bugs.php.net/bug.php?id=71798
