# [H] CVE-2017-18234

## Summary
Severity: High
Advisory: CVE-2017-18234
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18234
Type: osv

## Details
An issue was discovered in Exempi before 2.4.3. It allows remote attackers to cause a denial of service (invalid memcpy with resultant use-after-free) or possibly have unspecified other impact via a .pdf file containing JPEG data, related to XMPFiles/source/FormatSupport/ReconcileTIFF.cpp, XMPFiles/source/FormatSupport/TIFF_MemoryReader.cpp, and XMPFiles/source/FormatSupport/TIFF_Support.hpp.

## References
- https://usn.ubuntu.com/3668-1/
- https://access.redhat.com/errata/RHSA-2019:2048
- https://lists.debian.org/debian-lts-announce/2018/03/msg00013.html
- https://bugs.freedesktop.org/show_bug.cgi?id=100397
- https://cgit.freedesktop.org/exempi/commit/?id=c26d5beb60a5a85f76259f50ed3e08c8169b0a0c
