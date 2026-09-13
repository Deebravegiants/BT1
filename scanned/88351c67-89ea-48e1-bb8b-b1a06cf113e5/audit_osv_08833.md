# [C] CVE-2016-6295

## Summary
Severity: Critical
Advisory: CVE-2016-6295
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6295
Type: osv

## Details
ext/snmp/snmp.c in PHP before 5.5.38, 5.6.x before 5.6.24, and 7.x before 7.0.9 improperly interacts with the unserialize implementation and garbage collection, which allows remote attackers to cause a denial of service (use-after-free and application crash) or possibly have unspecified other impact via crafted serialized data, a related issue to CVE-2016-5773.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=cab1c3b3708eead315e033359d07049b23b147a3
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://www.securitytracker.com/id/1036430
- https://support.apple.com/HT207170
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.securityfocus.com/bid/92094
- https://security.gentoo.org/glsa/201611-22
- http://openwall.com/lists/oss-security/2016/07/24/2
- https://bugs.php.net/72479
