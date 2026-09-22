# [H] CVE-2016-2123

## Summary
Severity: High
Advisory: CVE-2016-2123
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-01
Source: https://osv.dev/vulnerability/CVE-2016-2123
Type: osv

## Details
A flaw was found in samba versions 4.0.0 to 4.5.2. The Samba routine ndr_pull_dnsp_name contains an integer wrap problem, leading to an attacker-controlled memory overwrite. ndr_pull_dnsp_name parses data from the Samba Active Directory ldb database. Any user who can write to the dnsRecord attribute over LDAP can trigger this memory corruption. By default, all authenticated LDAP users can write to the dnsRecord attribute on new DNS objects. This makes the defect a remote privilege escalation.

## References
- http://www.securityfocus.com/bid/94970
- http://www.securitytracker.com/id/1037493
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-2123
- https://www.samba.org/samba/security/CVE-2016-2123.html
