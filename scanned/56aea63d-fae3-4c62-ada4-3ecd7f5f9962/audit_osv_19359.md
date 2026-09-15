# [M] CVE-2021-20300

## Summary
Severity: Medium
Advisory: CVE-2021-20300
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-20300
Type: osv

## Details
A flaw was found in OpenEXR's hufUncompress functionality in OpenEXR/IlmImf/ImfHuf.cpp. This flaw allows an attacker who can submit a crafted file that is processed by OpenEXR, to trigger an integer overflow. The highest threat from this vulnerability is to system availability.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=25562
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1939153
- https://github.com/AcademySoftwareFoundation/openexr/pull/836
