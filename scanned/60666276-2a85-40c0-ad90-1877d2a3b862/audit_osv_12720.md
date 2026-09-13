# [M] CVE-2018-14498

## Summary
Severity: Medium
Advisory: CVE-2018-14498
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2018-14498
Type: osv

## Details
get_8bit_row in rdbmp.c in libjpeg-turbo through 1.5.90 and MozJPEG through 3.3.1 allows attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted 8-bit BMP in which one or more of the color indices is out of range for the number of palette entries.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00015.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/F7YP4QUEYGHI4Q7GIAVFVKWQ7DJMBYLU/
- https://usn.ubuntu.com/4190-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00015.html
- https://access.redhat.com/errata/RHSA-2019:2052
- https://access.redhat.com/errata/RHSA-2019:3705
- https://lists.debian.org/debian-lts-announce/2019/03/msg00021.html
- https://github.com/libjpeg-turbo/libjpeg-turbo/commit/9c78a04df4e44ef6487eee99c4258397f4fdca55
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/258
- https://github.com/mozilla/mozjpeg/issues/299
