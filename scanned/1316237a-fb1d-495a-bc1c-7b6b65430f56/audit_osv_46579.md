# [H] CVE-2013-7456

## Summary
Severity: High
Advisory: CVE-2013-7456
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2013-7456
Type: osv

## Details
gd_interpolation.c in the GD Graphics Library (aka libgd) before 2.1.1, as used in PHP before 5.5.36, 5.6.x before 5.6.22, and 7.x before 7.0.7, allows remote attackers to cause a denial of service (out-of-bounds read) or possibly have unspecified other impact via a crafted image that is mishandled by the imagescale function.

## References
- http://php.net/ChangeLog-5.php
- http://php.net/ChangeLog-7.php
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3587
- http://www.debian.org/security/2016/dsa-3602
- http://www.openwall.com/lists/oss-security/2016/05/26/3
- http://www.ubuntu.com/usn/USN-3030-1
- https://bugs.php.net/bug.php?id=72227
- https://github.com/libgd/libgd/commit/4f65a3e4eedaffa1efcf9ee1eb08f0b504fbc31a
- https://github.com/php/php-src/commit/7a1aac3343af85b4af4df5f8844946eaa27394ab?w=1
- http://www.securityfocus.com/bid/90859
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05240731
