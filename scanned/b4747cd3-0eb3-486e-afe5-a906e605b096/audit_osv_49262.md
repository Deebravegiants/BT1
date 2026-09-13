# [M] CVE-2018-7730

## Summary
Severity: Medium
Advisory: CVE-2018-7730
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-7730
Type: osv

## Details
An issue was discovered in Exempi through 2.4.4. A certain case of a 0xffffffff length is mishandled in XMPFiles/source/FormatSupport/PSIR_FileWriter.cpp, leading to a heap-based buffer over-read in the PSD_MetaHandler::CacheFileData() function.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BCFXKOOATZ2B5G3G7EBXZWVZHEABN4ZV/
- https://lists.debian.org/debian-lts-announce/2018/03/msg00013.html
- https://usn.ubuntu.com/3668-1/
- https://access.redhat.com/errata/RHSA-2019:2048
- https://bugs.freedesktop.org/show_bug.cgi?id=105204
- https://cgit.freedesktop.org/exempi/commit/?id=6cbd34025e5fd3ba47b29b602096e456507ce83b
