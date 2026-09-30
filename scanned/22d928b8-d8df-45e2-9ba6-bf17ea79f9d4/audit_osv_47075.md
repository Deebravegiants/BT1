# [H] CVE-2015-8877

## Summary
Severity: High
Advisory: CVE-2015-8877
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-22
Source: https://osv.dev/vulnerability/CVE-2015-8877
Type: osv

## Details
The gdImageScaleTwoPass function in gd_interpolation.c in the GD Graphics Library (aka libgd) before 2.2.0, as used in PHP before 5.6.12, uses inconsistent allocate and free approaches, which allows remote attackers to cause a denial of service (memory consumption) via a crafted call, as demonstrated by a call to the PHP imagescale function.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3587
- http://www.ubuntu.com/usn/USN-2987-1
- https://bugs.php.net/bug.php?id=70064
- https://github.com/libgd/libgd/commit/4751b606fa38edc456d627140898a7ec679fcc24
- https://github.com/libgd/libgd/issues/173
- http://www.php.net/ChangeLog-5.php
