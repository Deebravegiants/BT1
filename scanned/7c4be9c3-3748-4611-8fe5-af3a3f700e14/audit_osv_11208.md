# [H] CVE-2017-6800

## Summary
Severity: High
Advisory: CVE-2017-6800
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6800
Type: osv

## Details
An issue was discovered in ytnef before 1.9.2. An invalid memory access (heap-based buffer over-read) can occur during handling of LONG data types, related to MAPIPrint() in libytnef.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- http://www.debian.org/security/2017/dsa-3846
- https://github.com/Yeraze/ytnef/commit/f98f5d4adc1c4bd4033638f6167c1bb95d642f89
- https://github.com/Yeraze/ytnef/issues/28
