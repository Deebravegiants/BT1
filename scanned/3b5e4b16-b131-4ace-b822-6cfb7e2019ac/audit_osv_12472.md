# [C] CVE-2018-12421

## Summary
Severity: Critical
Advisory: CVE-2018-12421
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-14
Source: https://osv.dev/vulnerability/CVE-2018-12421
Type: osv

## Details
LTB (aka LDAP Tool Box) Self Service Password before 1.3 allows a change to a user password (without knowing the old password) via a crafted POST request, because the ldap_bind return value is mishandled and the PHP data type is not constrained to be a string.

## References
- https://github.com/ltb-project/self-service-password/issues/209
- https://github.com/ltb-project/self-service-password/issues/211
- https://lists.ltb-project.org/pipermail/ltb-announce/2018-June/000023.html
