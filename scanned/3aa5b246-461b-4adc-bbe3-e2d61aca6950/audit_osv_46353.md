# [C] CVE-2004-2154

## Summary
Severity: Critical
Advisory: CVE-2004-2154
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2004-12-31
Source: https://osv.dev/vulnerability/CVE-2004-2154
Type: osv

## Details
CUPS before 1.1.21rc1 treats a Location directive in cupsd.conf as case sensitive, which allows attackers to bypass intended ACLs via a printer name containing uppercase or lowercase letters that are different from what is specified in the directive.

## References
- http://www.novell.com/linux/security/advisories/2005_18_sr.html
- http://www.ubuntu.com/usn/usn-185-1
- https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=162405
- http://www.cups.org/str.php?L700
- https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=162405
- https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=163274
- http://www.cups.org/str.php?L700
- http://www.redhat.com/support/errata/RHSA-2005-571.html
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A9940
