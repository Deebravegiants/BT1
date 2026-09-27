# [H] CVE-2017-6802

## Summary
Severity: High
Advisory: CVE-2017-6802
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/CVE-2017-6802
Type: osv

## Details
An issue was discovered in ytnef before 1.9.2. There is a potential heap-based buffer over-read on incoming Compressed RTF Streams, related to DecompressRTF() in libytnef.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- http://www.debian.org/security/2017/dsa-3846
- https://github.com/Yeraze/ytnef/commit/22f8346c8d4f0020a40d9f258fdb3bfc097359cc
- https://github.com/Yeraze/ytnef/issues/34
