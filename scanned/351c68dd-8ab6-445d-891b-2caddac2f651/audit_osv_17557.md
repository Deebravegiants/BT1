# [M] CVE-2020-16588

## Summary
Severity: Medium
Advisory: CVE-2020-16588
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-16588
Type: osv

## Details
A Null Pointer Deference issue exists in Academy Software Foundation OpenEXR 2.3.0 in generatePreview in makePreview.cpp that can cause a denial of service via a crafted EXR file.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://github.com/AcademySoftwareFoundation/openexr/commit/74504503cff86e986bac441213c403b0ba28d58f
- https://github.com/AcademySoftwareFoundation/openexr/issues/493
