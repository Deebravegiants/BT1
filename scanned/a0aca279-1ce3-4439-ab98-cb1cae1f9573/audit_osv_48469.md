# [H] CVE-2017-7853

## Summary
Severity: High
Advisory: CVE-2017-7853
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-13
Source: https://osv.dev/vulnerability/CVE-2017-7853
Type: osv

## Details
In libosip2 in GNU oSIP 4.1.0 and 5.0.0, a malformed SIP message can lead to a heap buffer overflow in the msg_osip_body_parse() function defined in osipparser2/osip_message_parse.c, resulting in a remote DoS.

## References
- http://www.debian.org/security/2017/dsa-3879
- http://www.securityfocus.com/bid/97644
- https://savannah.gnu.org/support/index.php?109265
