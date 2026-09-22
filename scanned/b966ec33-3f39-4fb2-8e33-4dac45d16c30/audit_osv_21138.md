# [C] CVE-2021-40874

## Summary
Severity: Critical
Advisory: CVE-2021-40874
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-18
Source: https://osv.dev/vulnerability/CVE-2021-40874
Type: osv

## Details
An issue was discovered in LemonLDAP::NG (aka lemonldap-ng) 2.0.13. When using the RESTServer plug-in to operate a REST password validation service (for another LemonLDAP::NG instance, for example) and using the Kerberos authentication method combined with another method with the Combination authentication plug-in, any password will be recognized as valid for an existing user.

## References
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2612
