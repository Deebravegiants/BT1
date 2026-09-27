# [M] CVE-2018-19478

## Summary
Severity: Medium
Advisory: CVE-2018-19478
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2018-19478
Type: osv

## Details
In Artifex Ghostscript before 9.26, a carefully crafted PDF file can trigger an extremely long running computation when parsing the file.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=0a7e5a1c309fa0911b892fa40996a7d55d90bace
- https://lists.debian.org/debian-lts-announce/2018/12/msg00019.html
- https://www.ghostscript.com/doc/9.26/History9.htm
- http://www.securityfocus.com/bid/106445
- https://bugs.ghostscript.com/show_bug.cgi?id=699856
- https://bugzilla.redhat.com/show_bug.cgi?id=1655607
