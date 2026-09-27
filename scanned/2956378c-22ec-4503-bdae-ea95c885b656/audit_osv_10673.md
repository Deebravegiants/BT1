# [C] CVE-2017-18187

## Summary
Severity: Critical
Advisory: CVE-2017-18187
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-14
Source: https://osv.dev/vulnerability/CVE-2017-18187
Type: osv

## Details
In ARM mbed TLS before 2.7.0, there is a bounds-check bypass through an integer overflow in PSK identity parsing in the ssl_parse_client_psk_identity() function in library/ssl_srv.c.

## References
- https://usn.ubuntu.com/4267-1/
- http://www.securityfocus.com/bid/103055
- https://github.com/ARMmbed/mbedtls/blob/master/ChangeLog
- https://security.gentoo.org/glsa/201804-19
- https://www.debian.org/security/2018/dsa-4138
- https://www.debian.org/security/2018/dsa-4147
- https://github.com/ARMmbed/mbedtls/commit/83c9f495ffe70c7dd280b41fdfd4881485a3bc28
