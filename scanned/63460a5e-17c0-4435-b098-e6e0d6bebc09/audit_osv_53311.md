# [H] CVE-2022-37706

## Summary
Severity: High
Advisory: CVE-2022-37706
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2022-37706
Type: osv

## Details
enlightenment_sys in Enlightenment before 0.25.4 allows local users to gain privileges because it is setuid root, and the system library function mishandles pathnames that begin with a /dev/.. substring.

## References
- https://git.enlightenment.org/enlightenment/enlightenment/commit/cae78cbb169f237862faef123e4abaf63a1f5064
- https://git.enlightenment.org/enlightenment/enlightenment/commit/cc7faeccf77fef8b0ae70e312a21e4cde087e141
- https://github.com/MaherAzzouzi/CVE-2022-37706-LPE-exploit
