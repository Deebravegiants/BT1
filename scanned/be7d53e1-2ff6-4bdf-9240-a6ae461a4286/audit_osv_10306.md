# [M] CVE-2017-14864

## Summary
Severity: Medium
Advisory: CVE-2017-14864
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-29
Source: https://osv.dev/vulnerability/CVE-2017-14864
Type: osv

## Details
An Invalid memory address dereference was discovered in Exiv2::getULong in types.cpp in Exiv2 0.26. The vulnerability causes a segmentation fault and application crash, which leads to denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://usn.ubuntu.com/3852-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1494467
