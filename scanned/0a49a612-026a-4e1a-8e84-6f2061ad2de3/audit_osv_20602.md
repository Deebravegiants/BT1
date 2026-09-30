# [C] CVE-2021-35473

## Summary
Severity: Critical
Advisory: CVE-2021-35473
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-11-10
Source: https://osv.dev/vulnerability/CVE-2021-35473
Type: osv

## Details
An issue was discovered in LemonLDAP::NG before 2.0.12. There is a missing expiration check in the OAuth2.0 handler, i.e., it does not verify access token validity. An attacker can use a expired access token from an OIDC client to access the OAuth2 handler The earliest affected version is 2.0.4.

## References
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/tags
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2549
