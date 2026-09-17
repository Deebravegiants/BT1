# [H] CVE-2018-17281

## Summary
Severity: High
Advisory: CVE-2018-17281
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-24
Source: https://osv.dev/vulnerability/CVE-2018-17281
Type: osv

## Details
There is a stack consumption vulnerability in the res_http_websocket.so module of Asterisk through 13.23.0, 14.7.x through 14.7.7, and 15.x through 15.6.0 and Certified Asterisk through 13.21-cert2. It allows an attacker to crash Asterisk via a specially crafted HTTP request to upgrade the connection to a websocket.

## References
- http://packetstormsecurity.com/files/149453/Asterisk-Project-Security-Advisory-AST-2018-009.html
- http://www.securityfocus.com/bid/105389
- http://www.securitytracker.com/id/1041694
- https://lists.debian.org/debian-lts-announce/2018/09/msg00034.html
- https://security.gentoo.org/glsa/201811-11
- https://www.debian.org/security/2018/dsa-4320
- https://issues.asterisk.org/jira/browse/ASTERISK-28013
- http://downloads.asterisk.org/pub/security/AST-2018-009.html
- http://seclists.org/fulldisclosure/2018/Sep/31
- https://seclists.org/bugtraq/2018/Sep/53
