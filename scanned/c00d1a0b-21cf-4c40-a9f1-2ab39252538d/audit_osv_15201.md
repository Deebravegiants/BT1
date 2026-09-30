# [M] CVE-2019-14443

## Summary
Severity: Medium
Advisory: CVE-2019-14443
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-30
Source: https://osv.dev/vulnerability/CVE-2019-14443
Type: osv

## Details
An issue was discovered in Libav 12.3. Division by zero in range_decode_culshift in libavcodec/apedec.c allows remote attackers to cause a denial of service (application crash), as demonstrated by avconv.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00003.html
- https://bugzilla.libav.org/show_bug.cgi?id=1161#c1
