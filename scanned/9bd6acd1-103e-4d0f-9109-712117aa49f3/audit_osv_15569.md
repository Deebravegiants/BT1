# [M] CVE-2019-17402

## Summary
Severity: Medium
Advisory: CVE-2019-17402
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-17402
Type: osv

## Details
Exiv2 0.27.2 allows attackers to trigger a crash in Exiv2::getULong in types.cpp when called from Exiv2::Internal::CiffDirectory::readDirectory in crwimage_int.cpp, because there is no validation of the relationship of the total size to the offset and size.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00001.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/4159-1/
- https://github.com/Exiv2/exiv2/issues/1019
