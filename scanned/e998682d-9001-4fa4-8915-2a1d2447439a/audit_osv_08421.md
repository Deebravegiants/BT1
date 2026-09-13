# [M] CVE-2016-3120

## Summary
Severity: Medium
Advisory: CVE-2016-3120
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-01
Source: https://osv.dev/vulnerability/CVE-2016-3120
Type: osv

## Details
The validate_as_request function in kdc_util.c in the Key Distribution Center (KDC) in MIT Kerberos 5 (aka krb5) before 1.13.6 and 1.4.x before 1.14.3, when restrict_anonymous_to_tgt is enabled, uses an incorrect client data structure, which allows remote authenticated users to cause a denial of service (NULL pointer dereference and daemon crash) via an S4U2Self request.

## References
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00035.html
- http://web.mit.edu/kerberos/krb5-1.13/
- http://web.mit.edu/kerberos/krb5-1.14/
- http://www.securityfocus.com/bid/92132
- http://www.securitytracker.com/id/1036442
- https://lists.debian.org/debian-lts-announce/2018/01/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AWL3KYFRJIX37EAM4DKCQQIQP2WBKL35/
- http://rhn.redhat.com/errata/RHSA-2016-2591.html
- http://krbdev.mit.edu/rt/Ticket/Display.html?id=8458
- https://github.com/krb5/krb5/commit/93b4a6306a0026cf1cc31ac4bd8a49ba5d034ba7
