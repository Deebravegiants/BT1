# [H] CVE-2020-15395

## Summary
Severity: High
Advisory: CVE-2020-15395
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-15395
Type: osv

## Details
In MediaInfoLib in MediaArea MediaInfo 20.03, there is a stack-based buffer over-read in Streams_Fill_PerStream in Multiple/File_MpegPs.cpp (aka an off-by-one during MpegPs parsing).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QQJCEQRRPTN5CY5URDFTEJU3A2VKLNBA/
- https://mediaarea.net/en/MediaInfo
- https://sourceforge.net/p/mediainfo/bugs/1127/
