# [M] CVE-2017-9474

## Summary
Severity: Medium
Advisory: CVE-2017-9474
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-07
Source: https://osv.dev/vulnerability/CVE-2017-9474
Type: osv

## Details
In ytnef 1.9.2, the DecompressRTF function in lib/ytnef.c allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFJWMUEUC4ILH2HEOCYVVLQT654ZMCGQ/
- https://blogs.gentoo.org/ago/2017/05/24/ytnef-heap-based-buffer-overflow-in-decompressrtf-ytnef-c/
