# [M] CVE-2021-20303

## Summary
Severity: Medium
Advisory: CVE-2021-20303
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-20303
Type: osv

## Details
A flaw found in function dataWindowForTile() of IlmImf/ImfTiledMisc.cpp. An attacker who is able to submit a crafted file to be processed by OpenEXR could trigger an integer overflow, leading to an out-of-bounds write on the heap. The greatest impact of this flaw is to application availability, with some potential impact to data integrity as well.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25505
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1939151
- https://github.com/AcademySoftwareFoundation/openexr/pull/831
