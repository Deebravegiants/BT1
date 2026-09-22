# [C] CVE-2019-6978

## Summary
Severity: Critical
Advisory: CVE-2019-6978
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-28
Source: https://osv.dev/vulnerability/CVE-2019-6978
Type: osv

## Details
The GD Graphics Library (aka LibGD) 2.2.5 has a double free in the gdImage*Ptr() functions in gd_gif_out.c, gd_jpeg.c, and gd_wbmp.c. NOTE: PHP is unaffected.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00031.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3CZ2QADQTKRHTGB2AHD7J4QQNDLBEMM6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3WRUPZVT2MWFUEMVGTRAGDOBHLNMGK5R/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TEYUUOW75YD3DENIPYMO263E6NL2NFHI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TTXSLRZI5BCQT3H5KALG3DHUWUMNPDX2/
- https://access.redhat.com/errata/RHSA-2019:2722
- https://lists.debian.org/debian-lts-announce/2019/01/msg00028.html
- https://security.gentoo.org/glsa/201903-18
- https://usn.ubuntu.com/3900-1/
- https://www.debian.org/security/2019/dsa-4384
- https://github.com/libgd/libgd/commit/553702980ae89c83f2d6e254d62cf82e204956d0
- https://github.com/libgd/libgd/issues/492
- https://github.com/php/php-src/commit/089f7c0bc28d399b0420aa6ef058e4c1c120b2ae
