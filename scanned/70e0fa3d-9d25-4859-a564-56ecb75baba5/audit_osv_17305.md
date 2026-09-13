# [M] CVE-2020-14403

## Summary
Severity: Medium
Advisory: CVE-2020-14403
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2020-14403
Type: osv

## Details
An issue was discovered in LibVNCServer before 0.9.13. libvncserver/hextile.c allows out-of-bounds access via encodings.

## References
- https://github.com/LibVNC/libvncserver/compare/LibVNCServer-0.9.12...LibVNCServer-0.9.13
- https://lists.debian.org/debian-lts-announce/2020/06/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00045.html
- https://usn.ubuntu.com/4434-1/
- https://usn.ubuntu.com/4573-1/
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://github.com/LibVNC/libvncserver/commit/74e8a70f2c9a5248d6718ce443e07c7ed314dfff
