# [M] CVE-2017-14166

## Summary
Severity: Medium
Advisory: CVE-2017-14166
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-06
Source: https://osv.dev/vulnerability/CVE-2017-14166
Type: osv

## Details
libarchive 3.3.2 allows remote attackers to cause a denial of service (xml_data heap-based buffer over-read and application crash) via a crafted xar archive, related to the mishandling of empty strings in the atol8 function in archive_read_support_format_xar.c.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://security.gentoo.org/glsa/201908-11
- https://usn.ubuntu.com/3736-1/
- https://www.debian.org/security/2018/dsa-4360
- https://blogs.gentoo.org/ago/2017/09/06/libarchive-heap-based-buffer-overflow-in-xml_data-archive_read_support_format_xar-c/
- https://github.com/libarchive/libarchive/commit/fa7438a0ff4033e4741c807394a9af6207940d71
