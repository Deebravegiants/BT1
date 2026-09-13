# [M] CVE-2017-18238

## Summary
Severity: Medium
Advisory: CVE-2017-18238
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18238
Type: osv

## Details
An issue was discovered in Exempi before 2.4.4. The TradQT_Manager::ParseCachedBoxes function in XMPFiles/source/FormatSupport/QuickTime_Support.cpp allows remote attackers to cause a denial of service (infinite loop) via crafted XMP data in a .qt file.

## References
- https://usn.ubuntu.com/3668-1/
- https://access.redhat.com/errata/RHSA-2019:2048
- https://lists.debian.org/debian-lts-announce/2018/03/msg00013.html
- https://bugs.freedesktop.org/show_bug.cgi?id=102483
- https://cgit.freedesktop.org/exempi/commit/?id=886cd1d2314755adb1f4cdb99c16ff00830f0331
