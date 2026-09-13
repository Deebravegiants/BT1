# [M] CVE-2020-16587

## Summary
Severity: Medium
Advisory: CVE-2020-16587
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16587
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in Academy Software Foundation OpenEXR 2.3.0 in chunkOffsetReconstruction in ImfMultiPartInputFile.cpp that can cause a denial of service via a crafted EXR file.

## References
- https://lists.debian.org/debian-lts-announce/2021/07/msg00001.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://github.com/AcademySoftwareFoundation/openexr/issues/491
- https://github.com/AcademySoftwareFoundation/openexr/commit/8b5370c688a7362673c3a5256d93695617a4cd9a
