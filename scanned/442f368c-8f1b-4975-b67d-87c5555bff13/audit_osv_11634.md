# [H] CVE-2017-9146

## Summary
Severity: High
Advisory: CVE-2017-9146
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-22
Source: https://osv.dev/vulnerability/CVE-2017-9146
Type: osv

## Details
The TNEFFillMapi function in lib/ytnef.c in libytnef in ytnef through 1.9.2 does not ensure a nonzero count value before a certain memory allocation, which allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted tnef file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- https://usn.ubuntu.com/3667-1/
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=862707
- https://github.com/Yeraze/ytnef/issues/47
