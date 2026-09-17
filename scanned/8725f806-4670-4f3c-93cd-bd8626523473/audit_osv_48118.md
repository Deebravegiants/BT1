# [M] CVE-2017-18235

## Summary
Severity: Medium
Advisory: CVE-2017-18235
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-15
Source: https://osv.dev/vulnerability/CVE-2017-18235
Type: osv

## Details
An issue was discovered in Exempi before 2.4.3. The VPXChunk class in XMPFiles/source/FormatSupport/WEBP_Support.cpp does not ensure nonzero widths and heights, which allows remote attackers to cause a denial of service (assertion failure and application exit) via a crafted .webp file.

## References
- https://bugs.freedesktop.org/show_bug.cgi?id=101913
- https://cgit.freedesktop.org/exempi/commit/?id=9e76a7782a54a242f18d609e7ba32bf1c430a5e4
