# [M] CVE-2016-2126

## Summary
Severity: Medium
Advisory: CVE-2016-2126
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/CVE-2016-2126
Type: osv

## Details
Samba version 4.0.0 up to 4.5.2 is vulnerable to privilege elevation due to incorrect handling of the PAC (Privilege Attribute Certificate) checksum. A remote, authenticated, attacker can cause the winbindd process to crash using a legitimate Kerberos ticket. A local service with access to the winbindd privileged pipe can cause winbindd to cache elevated access permissions.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0494.html
- http://rhn.redhat.com/errata/RHSA-2017-0495.html
- http://rhn.redhat.com/errata/RHSA-2017-0662.html
- http://rhn.redhat.com/errata/RHSA-2017-0744.html
- http://www.securityfocus.com/bid/94994
- http://www.securitytracker.com/id/1037495
- https://access.redhat.com/errata/RHSA-2017:1265
- https://kb.pulsesecure.net/articles/Pulse_Security_Advisories/SA43730
- https://www.samba.org/samba/security/CVE-2016-2126.html
