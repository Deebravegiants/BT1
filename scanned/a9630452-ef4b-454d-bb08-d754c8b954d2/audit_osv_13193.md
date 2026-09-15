# [H] CVE-2018-18557

## Summary
Severity: High
Advisory: CVE-2018-18557
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-22
Source: https://osv.dev/vulnerability/CVE-2018-18557
Type: osv

## Details
LibTIFF 3.9.3, 3.9.4, 3.9.5, 3.9.6, 3.9.7, 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0beta7, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6, 4.0.7, 4.0.8 and 4.0.9 (with JBIG enabled) decodes arbitrarily-sized JBIG into a buffer, ignoring the buffer size, which leads to a tif_jbig.c JBIGDecode out-of-bounds write.

## References
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2018-18557
- https://usn.ubuntu.com/3906-2/
- https://access.redhat.com/errata/RHSA-2019:2053
- https://gitlab.com/libtiff/libtiff/merge_requests/38
- https://lists.debian.org/debian-lts-announce/2018/10/msg00019.html
- https://security.gentoo.org/glsa/201904-15
- https://usn.ubuntu.com/3864-1/
- https://www.debian.org/security/2018/dsa-4349
- https://gitlab.com/libtiff/libtiff/commit/681748ec2f5ce88da5f9fa6831e1653e46af8a66
- https://www.exploit-db.com/exploits/45694/
