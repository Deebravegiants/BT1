# [H] CVE-2016-6128

## Summary
Severity: High
Advisory: CVE-2016-6128
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-6128
Type: osv

## Details
The gdImageCropThreshold function in gd_crop.c in the GD Graphics Library (aka libgd) before 2.2.3, as used in PHP before 7.0.9, allows remote attackers to cause a denial of service (application crash) via an invalid color index.

## References
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00086.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00078.html
- http://rhn.redhat.com/errata/RHSA-2016-2750.html
- http://www.debian.org/security/2016/dsa-3619
- http://www.openwall.com/lists/oss-security/2016/06/30/1
- http://www.securityfocus.com/bid/91509
- http://www.securitytracker.com/id/1036276
- http://www.ubuntu.com/usn/USN-3030-1
- https://libgd.github.io/release-2.2.3.html
- https://security.gentoo.org/glsa/201612-09
- https://bugs.php.net/72494
- https://github.com/libgd/libgd/commit/6ff72ae40c7c20ece939afb362d98cc37f4a1c96
- https://github.com/libgd/libgd/commit/1ccfe21e14c4d18336f9da8515cd17db88c3de61
