# [M] CVE-2016-6292

## Summary
Severity: Medium
Advisory: CVE-2016-6292
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-07-25
Source: https://osv.dev/vulnerability/CVE-2016-6292
Type: osv

## Details
The exif_process_user_comment function in ext/exif/exif.c in PHP before 5.5.38, 5.6.x before 5.6.24, and 7.x before 7.0.9 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted JPEG image.

## References
- http://git.php.net/?p=php-src.git%3Ba=commit%3Bh=41131cd41d2fd2e0c2f332a27988df75659c42e4
- http://lists.apple.com/archives/security-announce/2016/Sep/msg00006.html
- http://www.securitytracker.com/id/1036430
- https://support.apple.com/HT207170
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3631
- http://www.securityfocus.com/bid/92078
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/72618
- http://openwall.com/lists/oss-security/2016/07/24/2
