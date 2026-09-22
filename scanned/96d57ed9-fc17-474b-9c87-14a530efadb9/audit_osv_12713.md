# [H] CVE-2018-14446

## Summary
Severity: High
Advisory: CVE-2018-14446
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-20
Source: https://osv.dev/vulnerability/CVE-2018-14446
Type: osv

## Details
MP4Integer32Property::Read in atom_avcC.cpp in MP4v2 2.1.0 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted MP4 file.

## References
- https://github.com/enzo1982/mp4v2/releases/tag/v2.1.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6YCHVOYPIBGM5HYUMQ77KZH2IHSITKVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FRSO2IMK6P7MOIZWGWKONPIEHKBA7WL3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GISUIWPKBWPXORUFNWBGFTKQS7UUVUC4/
- http://hac425.unaux.com/index.php/archives/63/
- https://github.com/TechSmith/mp4v2/issues/20
