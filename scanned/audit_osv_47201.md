# [H] CVE-2016-10326

## Summary
Severity: High
Advisory: CVE-2016-10326
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-13
Source: https://osv.dev/vulnerability/CVE-2016-10326
Type: osv

## Details
In libosip2 in GNU oSIP 4.1.0, a malformed SIP message can lead to a heap buffer overflow in the osip_body_to_str() function defined in osipparser2/osip_body.c, resulting in a remote DoS.

## References
- http://www.securityfocus.com/bid/92921
- http://www.debian.org/security/2017/dsa-3879
- https://savannah.gnu.org/support/index.php?109132
