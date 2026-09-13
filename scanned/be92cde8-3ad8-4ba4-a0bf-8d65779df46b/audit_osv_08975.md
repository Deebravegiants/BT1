# [M] CVE-2016-7128

## Summary
Severity: Medium
Advisory: CVE-2016-7128
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-09-12
Source: https://osv.dev/vulnerability/CVE-2016-7128
Type: osv

## Details
The exif_process_IFD_in_TIFF function in ext/exif/exif.c in PHP before 5.6.25 and 7.x before 7.0.10 mishandles the case of a thumbnail offset that exceeds the file size, which allows remote attackers to obtain sensitive information from process memory via a crafted TIFF image.

## References
- http://www.securityfocus.com/bid/92564
- http://www.securitytracker.com/id/1036680
- https://www.tenable.com/security/tns-2016-19
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.php.net/ChangeLog-5.php
- http://www.php.net/ChangeLog-7.php
- https://security.gentoo.org/glsa/201611-22
- https://bugs.php.net/bug.php?id=72627
- https://github.com/php/php-src/commit/6dbb1ee46b5f4725cc6519abf91e512a2a10dfed?w=1
- http://openwall.com/lists/oss-security/2016/09/02/9
