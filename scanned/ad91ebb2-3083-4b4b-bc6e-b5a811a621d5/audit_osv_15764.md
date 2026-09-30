# [M] CVE-2019-19479

## Summary
Severity: Medium
Advisory: CVE-2019-19479
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-12-01
Source: https://osv.dev/vulnerability/CVE-2019-19479
Type: osv

## Details
An issue was discovered in OpenSC through 0.19.0 and 0.20.x through 0.20.0-rc3. libopensc/card-setcos.c has an incorrect read operation during parsing of a SETCOS file attribute.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NDSQLMZZYBHO5X3BK7D6E7E6NZIMZDI5/
- http://www.openwall.com/lists/oss-security/2019/12/29/1
- https://lists.debian.org/debian-lts-announce/2019/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00027.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=18693
- https://github.com/OpenSC/OpenSC/commit/c3f23b836e5a1766c36617fe1da30d22f7b63de2
