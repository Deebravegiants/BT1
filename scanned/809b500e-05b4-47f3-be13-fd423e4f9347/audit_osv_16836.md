# [M] CVE-2019-9959

## Summary
Severity: Medium
Advisory: CVE-2019-9959
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-22
Source: https://osv.dev/vulnerability/CVE-2019-9959
Type: osv

## Details
The JPXStream::init function in Poppler 0.78.0 and earlier doesn't check for negative values of stream length, leading to an Integer Overflow, thereby making it possible to allocate a large memory chunk on the heap, with a size controlled by an attacker, as demonstrated by pdftocairo.

## References
- http://www.securityfocus.com/bid/109342
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5ZOYOZTGU4RGZW4E63OZ7LW4SMPEWGBV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A6NX2XPMMV7O52F4NBNCHGILGJXM3OJZ/
- https://access.redhat.com/errata/RHSA-2019:2713
- https://gitlab.freedesktop.org/poppler/poppler/blob/master/NEWS
- https://lists.debian.org/debian-lts-announce/2019/10/msg00024.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00014.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00030.html
