# [H] CVE-2019-14817

## Summary
Severity: High
Advisory: CVE-2019-14817
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-03
Source: https://osv.dev/vulnerability/CVE-2019-14817
Type: osv

## Details
A flaw was found in, ghostscript versions prior to 9.50, in the .pdfexectoken and other procedures where it did not properly secure its privileged calls, enabling scripts to bypass `-dSAFER` restrictions. A specially crafted PostScript file could disable security protection and then have access to the file system, or execute arbitrary commands.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=cd1b1cacadac2479e291efe611979bdc1b3bdb19
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LBUC4DBBJTRFNCR3IODBV4IXB2C2HI3V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZP34D27RKYV2POJ3NJLSVCHUA5V5C45A/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6AATIHU32MYKUOXQDJQU4X4DDVL7NAY3/
- https://security.gentoo.org/glsa/202004-03
- https://www.debian.org/security/2019/dsa-4518
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00088.html
- https://access.redhat.com/errata/RHBA-2019:2824
- https://access.redhat.com/errata/RHSA-2019:2594
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00090.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00007.html
- https://seclists.org/bugtraq/2019/Sep/15
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14817
