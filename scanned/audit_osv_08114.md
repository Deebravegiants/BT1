# [M] CVE-2016-10349

## Summary
Severity: Medium
Advisory: CVE-2016-10349
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2016-10349
Type: osv

## Details
The archive_le32dec function in archive_endian.h in libarchive 3.2.2 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/100347
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://usn.ubuntu.com/3736-1/
- https://security.gentoo.org/glsa/201710-19
- https://www.debian.org/security/2018/dsa-4360
- https://github.com/libarchive/libarchive/issues/834
