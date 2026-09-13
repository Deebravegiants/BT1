# [C] CVE-2018-20749

## Summary
Severity: Critical
Advisory: CVE-2018-20749
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-30
Source: https://osv.dev/vulnerability/CVE-2018-20749
Type: osv

## Details
LibVNC before 0.9.12 contains a heap out-of-bounds write vulnerability in libvncserver/rfbserver.c. The fix for CVE-2018-15127 was incomplete.

## References
- http://www.securityfocus.com/bid/106825
- https://lists.debian.org/debian-lts-announce/2019/01/msg00029.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://usn.ubuntu.com/3877-1/
- https://usn.ubuntu.com/4547-1/
- https://usn.ubuntu.com/4587-1/
- https://github.com/LibVNC/libvncserver/issues/273
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://github.com/LibVNC/libvncserver/commit/15bb719c03cc70f14c36a843dcb16ed69b405707
- https://www.openwall.com/lists/oss-security/2018/12/10/8
