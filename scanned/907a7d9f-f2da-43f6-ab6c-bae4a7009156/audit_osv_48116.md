# [M] CVE-2017-18233

## Summary
Severity: Medium
Advisory: CVE-2017-18233
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18233
Type: osv

## Details
An issue was discovered in Exempi before 2.4.4. Integer overflow in the Chunk class in XMPFiles/source/FormatSupport/RIFF.cpp allows remote attackers to cause a denial of service (infinite loop) via crafted XMP data in a .avi file.

## References
- https://access.redhat.com/errata/RHSA-2019:2048
- https://lists.debian.org/debian-lts-announce/2018/03/msg00013.html
- https://usn.ubuntu.com/3668-1/
- https://bugs.freedesktop.org/show_bug.cgi?id=102151
- https://cgit.freedesktop.org/exempi/commit/?id=65a8492832b7335ffabd01f5f64d89dec757c260
