# [C] CVE-2021-43834

## Summary
Severity: Critical
Advisory: CVE-2021-43834
Aliases: GHSA-98rp-gx76-33ph
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-43834
Type: osv

## Details
eLabFTW is an electronic lab notebook manager for research teams. In versions prior to 4.2.0 there is a vulnerability which allows an attacker to authenticate as an existing user, if that user was created using a single sign-on authentication option such as LDAP or SAML. It impacts instances where LDAP or SAML is used for authentication instead of the (default) local password mechanism. Users should upgrade to at least version 4.2.0.

## References
- https://github.com/elabftw/elabftw/releases/tag/4.2.0
- https://github.com/elabftw/elabftw/security/advisories/GHSA-98rp-gx76-33ph
