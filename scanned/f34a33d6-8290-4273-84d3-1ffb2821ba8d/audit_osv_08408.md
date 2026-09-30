# [C] CVE-2016-3078

## Summary
Severity: Critical
Advisory: CVE-2016-3078
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-3078
Type: osv

## Details
Multiple integer overflows in php_zip.c in the zip extension in PHP before 7.0.6 allow remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted call to (1) getFromIndex or (2) getFromName in the ZipArchive class.

## References
- http://www.securitytracker.com/id/1035701
- https://php.net/ChangeLog-7.php
- https://security-tracker.debian.org/tracker/CVE-2016-3078
- https://bugs.php.net/bug.php?id=71923
- https://github.com/php/php-src/commit/3b8d4de300854b3517c7acb239b84f7726c1353c?w=1
- http://www.openwall.com/lists/oss-security/2016/04/28/1
- https://www.exploit-db.com/exploits/39742/
