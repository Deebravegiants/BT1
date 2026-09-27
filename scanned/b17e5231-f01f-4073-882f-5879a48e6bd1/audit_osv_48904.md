# [M] CVE-2018-18073

## Summary
Severity: Medium
Advisory: CVE-2018-18073
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/CVE-2018-18073
Type: osv

## Details
Artifex Ghostscript allows attackers to bypass a sandbox protection mechanism by leveraging exposure of system operators in the saved execution stack in an error object.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=34cc326eb2c5695833361887fe0b32e8d987741c
- https://lists.debian.org/debian-lts-announce/2018/10/msg00013.html
- https://access.redhat.com/errata/RHSA-2018:3834
- https://usn.ubuntu.com/3803-1/
- https://www.debian.org/security/2018/dsa-4336
- http://packetstormsecurity.com/files/149758/Ghostscript-Exposed-System-Operators.html
- http://www.openwall.com/lists/oss-security/2018/10/10/12
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1690
- https://bugs.ghostscript.com/show_bug.cgi?id=699927
