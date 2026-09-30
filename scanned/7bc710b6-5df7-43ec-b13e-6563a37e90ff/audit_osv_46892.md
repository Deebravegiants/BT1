# [H] CVE-2015-7703

## Summary
Severity: High
Advisory: CVE-2015-7703
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-07-24
Source: https://osv.dev/vulnerability/CVE-2015-7703
Type: osv

## Details
The "pidfile" or "driftfile" directives in NTP ntpd 4.2.x before 4.2.8p4, and 4.3.x before 4.3.77, when ntpd is configured to allow remote configuration, allows remote attackers with an IP address that is allowed to send configuration requests, and with knowledge of the remote configuration password to write to arbitrary files via the :config command.

## References
- http://rhn.redhat.com/errata/RHSA-2016-0780.html
- http://rhn.redhat.com/errata/RHSA-2016-2583.html
- http://support.ntp.org/bin/view/Main/NtpBug2902
- http://www.debian.org/security/2015/dsa-3388
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/77278
- http://www.securitytracker.com/id/1033951
- https://bugzilla.redhat.com/show_bug.cgi?id=1254547
- https://security.gentoo.org/glsa/201607-15
- https://security.netapp.com/advisory/ntap-20171004-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1254547
