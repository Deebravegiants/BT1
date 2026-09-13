# [H] CVE-2019-14812

## Summary
Severity: High
Advisory: CVE-2019-14812
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-14812
Type: osv

## Details
A flaw was found in all ghostscript versions 9.x before 9.50, in the .setuserparams2 procedure where it did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. A specially crafted PostScript file could disable security protection and then have access to the file system, or execute arbitrary commands.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBUC4DBBJTRFNCR3IODBV4IXB2C2HI3V/
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=885444fcbe10dc42787ecb76686c8ee4dd33bf33
- https://access.redhat.com/security/cve/cve-2019-14812
- https://security.gentoo.org/glsa/202004-03
- https://bugs.ghostscript.com/show_bug.cgi?id=701444
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14812
