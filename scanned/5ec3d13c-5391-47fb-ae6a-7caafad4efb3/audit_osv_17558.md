# [M] CVE-2020-16589

## Summary
Severity: Medium
Advisory: CVE-2020-16589
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16589
Type: osv

## Details
A head-based buffer overflow exists in Academy Software Foundation OpenEXR 2.3.0 in writeTileData in ImfTiledOutputFile.cpp that can cause a denial of service via a crafted EXR file.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://github.com/AcademySoftwareFoundation/openexr/issues/494
- https://github.com/AcademySoftwareFoundation/openexr/commit/6bb36714528a9563dd3b92720c5063a1284b86f8
