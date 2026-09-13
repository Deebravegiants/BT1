# [M] CVE-2018-7728

## Summary
Severity: Medium
Advisory: CVE-2018-7728
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7728
Type: osv

## Details
An issue was discovered in Exempi through 2.4.4. XMPFiles/source/FileHandlers/TIFF_Handler.cpp mishandles a case of a zero length, leading to a heap-based buffer over-read in the MD5Update() function in third-party/zuid/interfaces/MD5.cpp.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BCFXKOOATZ2B5G3G7EBXZWVZHEABN4ZV/
- https://usn.ubuntu.com/3668-1/
- https://lists.debian.org/debian-lts-announce/2018/03/msg00013.html
- https://bugs.freedesktop.org/show_bug.cgi?id=105205
- https://cgit.freedesktop.org/exempi/commit/?id=e163667a06a9b656a047b0ec660b871f29a83c9f
