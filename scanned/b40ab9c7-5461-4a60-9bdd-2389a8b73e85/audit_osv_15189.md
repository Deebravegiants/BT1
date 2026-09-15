# [H] CVE-2019-14351

## Summary
Severity: High
Advisory: CVE-2019-14351
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-28
Source: https://osv.dev/vulnerability/CVE-2019-14351
Type: osv

## Details
EspoCRM 5.6.4 is vulnerable to user password hash enumeration. A malicious authenticated attacker can brute-force a user password hash by 1 symbol at a time using specially crafted api/v1/User?filterList filters.

## References
- https://github.com/espocrm/espocrm/issues/1357
