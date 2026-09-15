# [M] CVE-2017-18236

## Summary
Severity: Medium
Advisory: CVE-2017-18236
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18236
Type: osv

## Details
An issue was discovered in Exempi before 2.4.4. The ASF_Support::ReadHeaderObject function in XMPFiles/source/FormatSupport/ASF_Support.cpp allows remote attackers to cause a denial of service (infinite loop) via a crafted .asf file.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00013.html
- https://usn.ubuntu.com/3668-1/
- https://access.redhat.com/errata/RHSA-2019:2048
- https://cgit.freedesktop.org/exempi/commit/?id=fe59605d3520bf2ca4e0a963d194f10e9fee5806
- https://bugs.freedesktop.org/show_bug.cgi?id=102484
