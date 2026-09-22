# [H] CVE-2018-6535

## Summary
Severity: High
Advisory: CVE-2018-6535
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2018-6535
Type: osv

## Details
An issue was discovered in Icinga 2.x through 2.8.1. The lack of a constant-time password comparison function can disclose the password to an attacker.

## References
- https://github.com/Icinga/icinga2/issues/4920
- https://github.com/Icinga/icinga2/pull/5715
