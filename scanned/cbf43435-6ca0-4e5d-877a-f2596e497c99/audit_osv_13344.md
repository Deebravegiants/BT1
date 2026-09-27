# [C] CVE-2018-19466

## Summary
Severity: Critical
Advisory: CVE-2018-19466
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2018-19466
Type: osv

## Details
A vulnerability was found in Portainer before 1.20.0. Portainer stores LDAP credentials, corresponding to a master password, in cleartext and allows their retrieval via API calls.

## References
- https://github.com/portainer/portainer/releases
- https://github.com/MauroEldritch/lempo
- https://github.com/portainer/portainer/pull/2488
