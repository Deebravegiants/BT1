# [M] CVE-2019-3838

## Summary
Severity: Medium
Advisory: CVE-2019-3838
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-3838
Type: osv

## Details
It was found that the forceput operator could be extracted from the DefineResource method in ghostscript before 9.27. A specially crafted PostScript file could use this flaw in order to, for example, have access to the file system outside of the constrains imposed by -dSAFER.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A43SRQAEHQCKSEMIBINHUNIGHTDCZD7F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ANBSCZABXQUEQWIKNWJ35IYX24M227EI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SVERLGEU3OV6RNZ2SIBXREWD3BF5H23N/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00018.html
- http://packetstormsecurity.com/files/152367/Slackware-Security-Advisory-ghostscript-Updates.html
- https://access.redhat.com/errata/RHSA-2019:0652
- https://access.redhat.com/errata/RHSA-2019:0971
- https://lists.debian.org/debian-lts-announce/2019/04/msg00021.html
- https://seclists.org/bugtraq/2019/Apr/28
- https://seclists.org/bugtraq/2019/Apr/4
- https://security.gentoo.org/glsa/202004-03
- https://www.debian.org/security/2019/dsa-4432
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3838
- https://bugs.ghostscript.com/show_bug.cgi?id=700576
