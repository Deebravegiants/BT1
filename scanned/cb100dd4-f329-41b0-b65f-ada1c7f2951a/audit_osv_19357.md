# [H] CVE-2021-20299

## Summary
Severity: High
Advisory: CVE-2021-20299
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-20299
Type: osv

## Details
A flaw was found in OpenEXR's Multipart input file functionality. A crafted multi-part input file with no actual parts can trigger a NULL pointer dereference. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25740
- https://bugzilla.redhat.com/show_bug.cgi?id=1939154
- https://github.com/AcademySoftwareFoundation/openexr/commit/25e9515b06a6bc293d871622b8cafaee7af84e0f
