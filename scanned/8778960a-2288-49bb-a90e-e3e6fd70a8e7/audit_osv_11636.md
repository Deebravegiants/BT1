# [C] CVE-2017-9148

## Summary
Severity: Critical
Advisory: CVE-2017-9148
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-29
Source: https://osv.dev/vulnerability/CVE-2017-9148
Type: osv

## Details
The TLS session cache in FreeRADIUS 2.1.1 through 2.1.7, 3.0.x before 3.0.14, 3.1.x before 2017-02-04, and 4.0.x before 2017-02-04 fails to reliably prevent resumption of an unauthenticated session, which allows remote attackers (such as malicious 802.1X supplicants) to bypass authentication via PEAP or TTLS.

## References
- http://freeradius.org/security.html
- http://www.securitytracker.com/id/1038576
- http://seclists.org/oss-sec/2017/q2/422
- http://www.securityfocus.com/bid/98734
- https://access.redhat.com/errata/RHSA-2017:1581
- https://security.gentoo.org/glsa/201706-27
