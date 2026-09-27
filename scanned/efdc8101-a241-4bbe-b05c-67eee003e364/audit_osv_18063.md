# [H] CVE-2020-23356

## Summary
Severity: High
Advisory: CVE-2020-23356
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-01-27
Source: https://osv.dev/vulnerability/CVE-2020-23356
Type: osv

## Details
dmin/kernel/api/login.class.phpin in nibbleblog v3.7.1c allows type juggling for login bypass because == is used instead of === for password hashes, which mishandles hashes that begin with 0e followed by exclusively numerical characters.

## References
- https://github.com/dignajar/nibbleblog/pull/148
