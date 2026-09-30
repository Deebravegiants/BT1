# [H] CVE-2017-1000456

## Summary
Severity: High
Advisory: CVE-2017-1000456
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-02
Source: https://osv.dev/vulnerability/CVE-2017-1000456
Type: osv

## Details
freedesktop.org libpoppler 0.60.1 fails to validate boundaries in TextPool::addWord, leading to overflow in subsequent calculations.

## References
- https://lists.debian.org/debian-lts-announce/2018/01/msg00001.html
- https://www.debian.org/security/2018/dsa-4097
- https://bugs.freedesktop.org/show_bug.cgi?id=103116
