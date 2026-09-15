# [M] CVE-2016-2125

## Summary
Severity: Medium
Advisory: CVE-2016-2125
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2016-2125
Type: osv

## Details
It was found that Samba before versions 4.5.3, 4.4.8, 4.3.13 always requested forwardable tickets when using Kerberos authentication. A service to which Samba authenticated using Kerberos could subsequently use the ticket to impersonate Samba to other services or domain users.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0494.html
- http://rhn.redhat.com/errata/RHSA-2017-0495.html
- http://rhn.redhat.com/errata/RHSA-2017-0662.html
- http://rhn.redhat.com/errata/RHSA-2017-0744.html
- http://www.securityfocus.com/bid/94988
- http://www.securitytracker.com/id/1037494
- https://access.redhat.com/errata/RHSA-2017:1265
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-2125
- https://www.samba.org/samba/security/CVE-2016-2125.html
