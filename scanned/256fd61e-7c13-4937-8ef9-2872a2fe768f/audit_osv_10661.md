# [C] CVE-2017-18021

## Summary
Severity: Critical
Advisory: CVE-2017-18021
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-05
Source: https://osv.dev/vulnerability/CVE-2017-18021
Type: osv

## Details
It was discovered that QtPass before 1.2.1, when using the built-in password generator, generates possibly predictable and enumerable passwords. This only applies to the QtPass GUI.

## References
- https://github.com/IJHack/QtPass/releases/tag/v1.2.1
- https://qtpass.org/
- https://lists.zx2c4.com/pipermail/password-store/2018-January/003165.html
- https://github.com/IJHack/QtPass/issues/338
