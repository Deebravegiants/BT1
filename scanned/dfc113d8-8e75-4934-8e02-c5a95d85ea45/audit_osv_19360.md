# [M] CVE-2021-20302

## Summary
Severity: Medium
Advisory: CVE-2021-20302
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-20302
Type: osv

## Details
A flaw was found in OpenEXR's TiledInputFile functionality. This flaw allows an attacker who can submit a crafted single-part non-image to be processed by OpenEXR, to trigger a floating-point exception error. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25894
- https://bugzilla.redhat.com/show_bug.cgi?id=1939161
- https://github.com/AcademySoftwareFoundation/openexr/pull/842
