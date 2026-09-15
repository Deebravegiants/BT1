# [M] CVE-2017-7982

## Summary
Severity: Medium
Advisory: CVE-2017-7982
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-20
Source: https://osv.dev/vulnerability/CVE-2017-7982
Type: osv

## Details
Integer overflow in the plist_from_bin function in bplist.c in libimobiledevice/libplist before 2017-04-19 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted plist file.

## References
- https://lists.debian.org/debian-lts-announce/2020/04/msg00002.html
- https://github.com/libimobiledevice/libplist/issues/103
