# [H] CVE-2017-6801

## Summary
Severity: High
Advisory: CVE-2017-6801
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6801
Type: osv

## Details
An issue was discovered in ytnef before 1.9.2. There is a potential out-of-bounds access with fields of Size 0 in TNEFParse() in libytnef.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- http://www.debian.org/security/2017/dsa-3846
- https://github.com/Yeraze/ytnef/commit/3cb0f914d6427073f262e1b2b5fd973e3043cdf7
