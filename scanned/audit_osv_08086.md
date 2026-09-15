# [M] CVE-2016-10209

## Summary
Severity: Medium
Advisory: CVE-2016-10209
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2016-10209
Type: osv

## Details
The archive_wstring_append_from_mbs function in archive_string.c in libarchive 3.2.2 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted archive file.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- https://usn.ubuntu.com/3736-1/
- http://www.securityfocus.com/bid/97327
- https://www.debian.org/security/2018/dsa-4360
- https://github.com/libarchive/libarchive/issues/842
