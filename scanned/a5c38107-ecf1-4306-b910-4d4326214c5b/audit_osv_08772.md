# [C] CVE-2016-5773

## Summary
Severity: Critical
Advisory: CVE-2016-5773
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5773
Type: osv

## Details
php_zip.c in the zip extension in PHP before 5.5.37, 5.6.x before 5.6.23, and 7.x before 7.0.8 improperly interacts with the unserialize implementation and garbage collection, which allows remote attackers to execute arbitrary code or cause a denial of service (use-after-free and application crash) via crafted serialized data containing a ZipArchive object.

## References
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00004.html
- http://www.securityfocus.com/bid/91397
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://support.apple.com/HT207170
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3618
- http://www.openwall.com/lists/oss-security/2016/06/23/4
- http://github.com/php/php-src/commit/f6aef68089221c5ea047d4a74224ee3deead99a6?w=1
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- https://bugs.php.net/bug.php?id=72434
