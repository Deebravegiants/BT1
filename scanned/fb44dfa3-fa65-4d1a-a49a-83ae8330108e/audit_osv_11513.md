# [M] CVE-2017-8301

## Summary
Severity: Medium
Advisory: CVE-2017-8301
CVSS: 5.3 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8301
Type: osv

## Details
LibreSSL 2.5.1 to 2.5.3 lacks TLS certificate verification if SSL_get_verify_result is relied upon for a later check of a verification result, in a use case where a user-provided verification callback returns 1, as demonstrated by acceptance of invalid certificates by nginx.

## References
- http://seclists.org/oss-sec/2017/q2/145
- http://www.securityfocus.com/bid/98076
- https://github.com/libressl-portable/portable/issues/307
- https://trac.nginx.org/nginx/ticket/1257
