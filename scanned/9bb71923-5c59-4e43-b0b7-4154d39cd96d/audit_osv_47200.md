# [H] CVE-2016-10325

## Summary
Severity: High
Advisory: CVE-2016-10325
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-13
Source: https://osv.dev/vulnerability/CVE-2016-10325
Type: osv

## Details
In libosip2 in GNU oSIP 4.1.0, a malformed SIP message can lead to a heap buffer overflow in the _osip_message_to_str() function defined in osipparser2/osip_message_to_str.c, resulting in a remote DoS.

## References
- http://www.securityfocus.com/bid/92921
- http://www.debian.org/security/2017/dsa-3879
- https://savannah.gnu.org/support/index.php?109131
