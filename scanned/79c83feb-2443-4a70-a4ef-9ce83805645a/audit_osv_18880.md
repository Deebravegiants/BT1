# [H] CVE-2020-36658

## Summary
Severity: High
Advisory: CVE-2020-36658
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-27
Source: https://osv.dev/vulnerability/CVE-2020-36658
Type: osv

## Details
In Apache::Session::LDAP before 0.5, validity of the X.509 certificate is not checked by default when connecting to remote LDAP backends, because the default configuration of the Net::LDAPS module for Perl is used. NOTE: this can, for example, be fixed in conjunction with the CVE-2020-16093 fix.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00024.html
- https://github.com/LemonLDAPNG/Apache-Session-LDAP/commit/490722b71eed1ed1ab33d58c78578f23e043561f
