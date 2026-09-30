# [H] CVE-2020-16093

## Summary
Severity: High
Advisory: CVE-2020-16093
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-07-18
Source: https://osv.dev/vulnerability/CVE-2020-16093
Type: osv

## Details
In LemonLDAP::NG (aka lemonldap-ng) through 2.0.8, validity of the X.509 certificate is not checked by default when connecting to remote LDAP backends, because the default configuration of the Net::LDAPS module for Perl is used.

## References
- https://lemonldap-ng.org/download
- https://lists.debian.org/debian-lts-announce/2023/01/msg00027.html
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2250
