# [H] CVE-2021-35472

## Summary
Severity: High
Advisory: CVE-2021-35472
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-35472
Type: osv

## Details
An issue was discovered in LemonLDAP::NG before 2.0.12. Session cache corruption can lead to authorization bypass or spoofing. By running a loop that makes many authentication attempts, an attacker might alternately be authenticated as one of two different users.

## References
- https://www.debian.org/security/2021/dsa-4943
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/commit/8d3b763b6af2b8a9c4ad2765fbfabffec8a73af5
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2539
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/tags
