# [C] CVE-2019-11187

## Summary
Severity: Critical
Advisory: CVE-2019-11187
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2019-11187
Type: osv

## Details
Incorrect Access Control in the LDAP class of GONICUS GOsa through 2019-04-11 allows an attacker to log into any account with a username containing the case-insensitive substring "success" when an arbitrary password is provided.

## References
- https://lists.debian.org/debian-lts-announce/2019/08/msg00009.html
- https://github.com/gonicus/gosa/commits/master
