# [H] CVE-2018-14326

## Summary
Severity: High
Advisory: CVE-2018-14326
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/CVE-2018-14326
Type: osv

## Details
In MP4v2 2.0.0, there is an integer overflow (with resultant memory corruption) when resizing MP4Array for the ftyp atom in mp4array.h.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6YCHVOYPIBGM5HYUMQ77KZH2IHSITKVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRSO2IMK6P7MOIZWGWKONPIEHKBA7WL3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GISUIWPKBWPXORUFNWBGFTKQS7UUVUC4/
- http://www.openwall.com/lists/oss-security/2018/07/16/1
