# [C] CVE-2018-14054

## Summary
Severity: Critical
Advisory: CVE-2018-14054
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-14054
Type: osv

## Details
A double free exists in the MP4StringProperty class in mp4property.cpp in MP4v2 2.0.0. A dangling pointer is freed again in the destructor once an exception is triggered.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6YCHVOYPIBGM5HYUMQ77KZH2IHSITKVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRSO2IMK6P7MOIZWGWKONPIEHKBA7WL3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GISUIWPKBWPXORUFNWBGFTKQS7UUVUC4/
- http://www.openwall.com/lists/oss-security/2018/07/13/1
