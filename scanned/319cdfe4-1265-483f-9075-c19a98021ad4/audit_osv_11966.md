# [H] CVE-2018-1000222

## Summary
Severity: High
Advisory: CVE-2018-1000222
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000222
Type: osv

## Details
Libgd version 2.2.5 contains a Double Free Vulnerability vulnerability in gdImageBmpPtr Function that can result in Remote Code Execution . This attack appear to be exploitable via Specially Crafted Jpeg Image can trigger double free. This vulnerability appears to have been fixed in after commit ac16bdf2d41724b5a65255d4c28fb0ec46bc42f5.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3CZ2QADQTKRHTGB2AHD7J4QQNDLBEMM6/
- https://lists.debian.org/debian-lts-announce/2019/01/msg00028.html
- https://security.gentoo.org/glsa/201903-18
- https://usn.ubuntu.com/3755-1/
- https://github.com/libgd/libgd/issues/447
