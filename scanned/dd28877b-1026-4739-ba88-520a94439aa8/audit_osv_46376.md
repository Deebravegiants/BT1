# [H] CVE-2007-4103

## Summary
Severity: High
Advisory: CVE-2007-4103
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2007-07-31
Source: https://osv.dev/vulnerability/CVE-2007-4103
Type: osv

## Details
The IAX2 channel driver (chan_iax2) in Asterisk Open 1.2.x before 1.2.23, 1.4.x before 1.4.9, and Asterisk Appliance Developer Kit before 0.6.0, when configured to allow unauthenticated calls, allows remote attackers to cause a denial of service (resource exhaustion) via a flood of calls that do not complete a 3-way handshake, which causes an ast_channel to be allocated but not released.

## References
- http://secunia.com/advisories/26274
- http://secunia.com/advisories/29051
- http://security.gentoo.org/glsa/glsa-200802-11.xml
- http://www.securityfocus.com/archive/1/475069/100/0/threaded
- http://www.securityfocus.com/bid/24950
- http://www.securitytracker.com/id?1018472
- http://www.vupen.com/english/advisories/2007/2701
- http://bugs.gentoo.org/show_bug.cgi?id=185713
- http://ftp.digium.com/pub/asa/ASA-2007-018.pdf
- http://secunia.com/advisories/26274
- http://bugs.gentoo.org/show_bug.cgi?id=185713
- http://ftp.digium.com/pub/asa/ASA-2007-018.pdf
- http://osvdb.org/38197
- http://securityreason.com/securityalert/2960
- http://www.securityfocus.com/archive/1/475069/100/0/threaded
- http://www.securityfocus.com/bid/24950
- http://www.securitytracker.com/id?1018472
