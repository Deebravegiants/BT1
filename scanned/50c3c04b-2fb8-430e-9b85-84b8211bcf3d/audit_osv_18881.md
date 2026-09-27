# [H] CVE-2020-36659

## Summary
Severity: High
Advisory: CVE-2020-36659
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-27
Source: https://osv.dev/vulnerability/CVE-2020-36659
Type: osv

## Details
In Apache::Session::Browseable before 1.3.6, validity of the X.509 certificate is not checked by default when connecting to remote LDAP backends, because the default configuration of the Net::LDAPS module for Perl is used. NOTE: this can, for example, be fixed in conjunction with the CVE-2020-16093 fix.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00025.html
- https://github.com/LemonLDAPNG/Apache-Session-Browseable/commit/fdf393235140b293cae5578ef136055a78f3574f
