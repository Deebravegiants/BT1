# [H] CVE-2018-14379

## Summary
Severity: High
Advisory: CVE-2018-14379
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-18
Source: https://osv.dev/vulnerability/CVE-2018-14379
Type: osv

## Details
MP4Atom::factory in mp4atom.cpp in MP4v2 2.0.0 incorrectly uses the MP4ItemAtom data type in a certain case where MP4DataAtom is required, which allows remote attackers to cause a denial of service (memory corruption) or possibly have unspecified other impact via a crafted MP4 file, because access to the data structure has different expectations about layout as a result of this type confusion.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6YCHVOYPIBGM5HYUMQ77KZH2IHSITKVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRSO2IMK6P7MOIZWGWKONPIEHKBA7WL3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GISUIWPKBWPXORUFNWBGFTKQS7UUVUC4/
- http://www.openwall.com/lists/oss-security/2018/07/17/1
