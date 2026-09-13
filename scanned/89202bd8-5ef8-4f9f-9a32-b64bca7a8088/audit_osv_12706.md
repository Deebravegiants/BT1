# [C] CVE-2018-14403

## Summary
Severity: Critical
Advisory: CVE-2018-14403
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14403
Type: osv

## Details
MP4NameFirstMatches in mp4util.cpp in MP4v2 2.0.0 mishandles substrings of atom names, leading to use of an inappropriate data type for associated atoms. The resulting type confusion can cause out-of-bounds memory access.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6YCHVOYPIBGM5HYUMQ77KZH2IHSITKVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRSO2IMK6P7MOIZWGWKONPIEHKBA7WL3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GISUIWPKBWPXORUFNWBGFTKQS7UUVUC4/
- http://www.openwall.com/lists/oss-security/2018/07/18/3
