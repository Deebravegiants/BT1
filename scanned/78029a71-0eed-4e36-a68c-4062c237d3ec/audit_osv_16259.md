# [H] CVE-2019-3839

## Summary
Severity: High
Advisory: CVE-2019-3839
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-05-16
Source: https://osv.dev/vulnerability/CVE-2019-3839
Type: osv

## Details
It was found that in ghostscript some privileged operators remained accessible from various places after the CVE-2019-6116 fix. A specially crafted PostScript file could use this flaw in order to, for example, have access to the file system outside of the constrains imposed by -dSAFER. Ghostscript versions before 9.27 are vulnerable.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=4ec9ca74bed49f2a82acb4bf430eae0d8b3b75c9
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6AATIHU32MYKUOXQDJQU4X4DDVL7NAY3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZP34D27RKYV2POJ3NJLSVCHUA5V5C45A/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00088.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00090.html
- https://access.redhat.com/errata/RHSA-2019:0971
- https://access.redhat.com/errata/RHSA-2019:1017
- https://lists.debian.org/debian-lts-announce/2019/05/msg00023.html
- https://seclists.org/bugtraq/2019/May/23
- https://usn.ubuntu.com/3970-1/
- https://www.debian.org/security/2019/dsa-4442
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3839
