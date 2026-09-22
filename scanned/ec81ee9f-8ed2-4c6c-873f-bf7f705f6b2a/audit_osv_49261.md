# [M] CVE-2018-7729

## Summary
Severity: Medium
Advisory: CVE-2018-7729
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7729
Type: osv

## Details
An issue was discovered in Exempi through 2.4.4. There is a stack-based buffer over-read in the PostScript_MetaHandler::ParsePSFile() function in XMPFiles/source/FileHandlers/PostScript_Handler.cpp.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BCFXKOOATZ2B5G3G7EBXZWVZHEABN4ZV/
- https://usn.ubuntu.com/3668-1/
- https://bugs.freedesktop.org/show_bug.cgi?id=105206
- https://cgit.freedesktop.org/exempi/commit/?id=baa4b8a02c1ffab9645d13f0bfb1c0d10d311a0c
