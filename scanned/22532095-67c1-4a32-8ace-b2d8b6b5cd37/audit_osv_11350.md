# [H] CVE-2017-7507

## Summary
Severity: High
Advisory: CVE-2017-7507
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2017-7507
Type: osv

## Details
GnuTLS version 3.5.12 and earlier is vulnerable to a NULL pointer dereference while decoding a status response TLS extension with valid contents. This could lead to a crash of the GnuTLS server application.

## References
- http://www.debian.org/security/2017/dsa-3884
- http://www.securityfocus.com/bid/99102
- https://access.redhat.com/errata/RHSA-2017:2292
- https://www.gnutls.org/security.html#GNUTLS-SA-2017-4
