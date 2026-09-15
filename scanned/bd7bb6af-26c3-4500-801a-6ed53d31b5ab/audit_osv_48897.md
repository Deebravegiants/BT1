# [H] CVE-2018-17961

## Summary
Severity: High
Advisory: CVE-2018-17961
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/CVE-2018-17961
Type: osv

## Details
Artifex Ghostscript 9.25 and earlier allows attackers to bypass a sandbox protection mechanism via vectors involving errorhandler setup. NOTE: this issue exists because of an incomplete fix for CVE-2018-17183.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=a5a9bf8c6a63
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=a6807394bd94
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=a54c9e61e7d0
- https://usn.ubuntu.com/3803-1/
- https://access.redhat.com/errata/RHSA-2018:3834
- https://lists.debian.org/debian-lts-announce/2018/10/msg00013.html
- https://www.debian.org/security/2018/dsa-4336
- https://bugs.ghostscript.com/show_bug.cgi?id=699816
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1682&desc=2
- http://www.openwall.com/lists/oss-security/2018/10/09/4
- https://www.exploit-db.com/exploits/45573/
