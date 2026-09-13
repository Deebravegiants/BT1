# [H] CVE-2017-7252

## Summary
Severity: High
Advisory: CVE-2017-7252
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-11-03
Source: https://osv.dev/vulnerability/CVE-2017-7252
Type: osv

## Details
bcrypt password hashing in Botan before 2.1.0 does not correctly handle passwords with a length between 57 and 72 characters, which makes it easier for attackers to determine the cleartext password.

## References
- https://botan.randombit.net/security.html
- https://bugzilla.suse.com/show_bug.cgi?id=1034591
