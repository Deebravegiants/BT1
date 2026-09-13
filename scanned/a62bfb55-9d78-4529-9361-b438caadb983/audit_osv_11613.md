# [C] CVE-2017-9058

## Summary
Severity: Critical
Advisory: CVE-2017-9058
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-18
Source: https://osv.dev/vulnerability/CVE-2017-9058
Type: osv

## Details
In libytnef in ytnef through 1.9.2, there is a heap-based buffer over-read due to incorrect boundary checking in the SIZECHECK macro in lib/ytnef.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- https://usn.ubuntu.com/3667-1/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=862556
