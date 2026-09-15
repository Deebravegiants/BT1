# [M] CVE-2015-8872

## Summary
Severity: Medium
Advisory: CVE-2015-8872
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-03
Source: https://osv.dev/vulnerability/CVE-2015-8872
Type: osv

## Details
The set_fat function in fat.c in dosfstools before 4.0 might allow attackers to corrupt a FAT12 filesystem or cause a denial of service (invalid memory read and crash) by writing an odd number of clusters to the third to last entry on a FAT12 filesystem, which triggers an "off-by-two error."

## References
- http://www.ubuntu.com/usn/USN-2986-1
- https://blog.fuzzing-project.org/44-dosfstools-fsck.vfat-Several-invalid-memory-accesses.html
- https://github.com/dosfstools/dosfstools/issues/12
- https://github.com/dosfstools/dosfstools/commit/07908124838afcc99c577d1d3e84cef2dbd39cb7
- https://github.com/dosfstools/dosfstools/releases/tag/v4.0
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00001.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00014.html
- http://www.securityfocus.com/bid/90311
- https://lists.debian.org/debian-lts-announce/2020/05/msg00028.html
