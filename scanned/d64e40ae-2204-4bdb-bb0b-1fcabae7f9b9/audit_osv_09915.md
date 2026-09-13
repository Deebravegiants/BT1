# [M] CVE-2017-12141

## Summary
Severity: Medium
Advisory: CVE-2017-12141
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-12141
Type: osv

## Details
In ytnef 1.9.2, a heap-based buffer overflow vulnerability was found in the function TNEFFillMapi in ytnef.c, which allows attackers to cause a denial of service via a crafted file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- https://usn.ubuntu.com/3667-1/
- https://somevulnsofadlab.blogspot.com/2017/07/ytnefheap-buffer-overflow-in.html
- https://github.com/Yeraze/ytnef/issues/50
