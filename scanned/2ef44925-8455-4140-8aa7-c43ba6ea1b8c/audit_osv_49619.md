# [C] CVE-2019-14813

## Summary
Severity: Critical
Advisory: CVE-2019-14813
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-14813
Type: osv

## Details
A flaw was found in ghostscript, versions 9.x before 9.50, in the setsystemparams procedure where it did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. A specially crafted PostScript file could disable security protection and then have access to the file system, or execute arbitrary commands.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6AATIHU32MYKUOXQDJQU4X4DDVL7NAY3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZP34D27RKYV2POJ3NJLSVCHUA5V5C45A/
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=885444fcbe10dc42787ecb76686c8ee4dd33bf33
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBUC4DBBJTRFNCR3IODBV4IXB2C2HI3V/
- https://seclists.org/bugtraq/2019/Sep/15
- https://security.gentoo.org/glsa/202004-03
- https://www.debian.org/security/2019/dsa-4518
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00088.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00090.html
- https://access.redhat.com/errata/RHBA-2019:2824
- https://access.redhat.com/errata/RHSA-2019:2594
- https://lists.debian.org/debian-lts-announce/2019/09/msg00007.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14813
