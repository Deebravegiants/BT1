# [H] CVE-2018-17183

## Summary
Severity: High
Advisory: CVE-2018-17183
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-19
Source: https://osv.dev/vulnerability/CVE-2018-17183
Type: osv

## Details
Artifex Ghostscript before 9.25 allowed a user-writable error exception table, which could be used by remote attackers able to supply crafted PostScript to potentially overwrite or replace error handlers to inject code.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=fb713b3818b52d8a6cf62c951eba2e1795ff9624
- https://usn.ubuntu.com/3773-1/
- https://access.redhat.com/errata/RHSA-2018:3834
- https://lists.debian.org/debian-lts-announce/2018/09/msg00038.html
- https://bugs.ghostscript.com/show_bug.cgi?id=699708
