# [C] CVE-2016-10324

## Summary
Severity: Critical
Advisory: CVE-2016-10324
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-13
Source: https://osv.dev/vulnerability/CVE-2016-10324
Type: osv

## Details
In libosip2 in GNU oSIP 4.1.0, a malformed SIP message can lead to a heap buffer overflow in the osip_clrncpy() function defined in osipparser2/osip_port.c.

## References
- http://www.debian.org/security/2017/dsa-3879
- http://www.securityfocus.com/bid/97641
- https://savannah.gnu.org/support/index.php?109133
