# [H] CVE-2009-0034

## Summary
Severity: High
Advisory: CVE-2009-0034
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2009-01-30
Source: https://osv.dev/vulnerability/CVE-2009-0034
Type: osv

## Details
parse.c in sudo 1.6.9p17 through 1.6.9p19 does not properly interpret a system group (aka %group) in the sudoers file during authorization decisions for a user who belongs to that group, which allows local users to leverage an applicable sudoers file and gain root privileges via a sudo command.

## References
- http://secunia.com/advisories/33753
- http://secunia.com/advisories/33840
- http://secunia.com/advisories/33885
- http://secunia.com/advisories/35766
- http://www.gratisoft.us/bugzilla/show_bug.cgi?id=327
- http://www.mandriva.com/security/advisories?name=MDVSA-2009:033
- http://www.securityfocus.com/archive/1/500546/100/0/threaded
- http://www.securityfocus.com/archive/1/504849/100/0/threaded
- http://www.securityfocus.com/bid/33517
- http://www.securitytracker.com/id?1021688
- http://www.vmware.com/security/advisories/VMSA-2009-0009.html
- http://www.gratisoft.us/bugzilla/show_bug.cgi?id=327
- http://www.vupen.com/english/advisories/2009/1865
- https://bugzilla.novell.com/show_bug.cgi?id=468923
- http://lists.vmware.com/pipermail/security-announce/2009/000060.html
- http://osvdb.org/51736
- http://wiki.rpath.com/Advisories:rPSA-2009-0021
- http://www.redhat.com/support/errata/RHSA-2009-0267.html
- http://www.securityfocus.com/archive/1/500546/100/0/threaded
- http://www.securityfocus.com/archive/1/504849/100/0/threaded
