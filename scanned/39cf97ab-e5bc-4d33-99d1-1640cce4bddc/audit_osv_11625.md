# [M] CVE-2017-9114

## Summary
Severity: Medium
Advisory: CVE-2017-9114
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-21
Source: https://osv.dev/vulnerability/CVE-2017-9114
Type: osv

## Details
In OpenEXR 2.2.0, an invalid read of size 1 in the refill function in ImfFastHuf.cpp could cause the application to crash.

## References
- https://github.com/openexr/openexr/releases/tag/v2.2.1
- https://lists.debian.org/debian-lts-announce/2020/08/msg00056.html
- http://www.openwall.com/lists/oss-security/2017/05/12/5
- https://www.debian.org/security/2020/dsa-4755
- https://github.com/openexr/openexr/issues/232
- https://github.com/openexr/openexr/pull/233
