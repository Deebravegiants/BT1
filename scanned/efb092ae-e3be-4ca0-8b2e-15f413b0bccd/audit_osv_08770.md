# [C] CVE-2016-5771

## Summary
Severity: Critical
Advisory: CVE-2016-5771
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5771
Type: osv

## Details
spl_array.c in the SPL extension in PHP before 5.5.37 and 5.6.x before 5.6.23 improperly interacts with the unserialize implementation and garbage collection, which allows remote attackers to execute arbitrary code or cause a denial of service (use-after-free and application crash) via crafted serialized data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00004.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00003.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3618
- http://www.securityfocus.com/bid/91401
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
- https://support.apple.com/HT207170
- https://bugs.php.net/bug.php?id=72433
- http://github.com/php/php-src/commit/3f627e580acfdaf0595ae3b115b8bec677f203ee?w=1
- http://php.net/ChangeLog-5.php
- http://www.openwall.com/lists/oss-security/2016/06/23/4
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
