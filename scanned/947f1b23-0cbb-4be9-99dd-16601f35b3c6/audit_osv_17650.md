# [M] CVE-2020-18651

## Summary
Severity: Medium
Advisory: CVE-2020-18651
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-18651
Type: osv

## Details
Buffer Overflow vulnerability in function ID3_Support::ID3v2Frame::getFrameValue in exempi 2.5.0 and earlier allows remote attackers to cause a denial of service via opening of crafted audio file with ID3V2 frame.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00032.html
- https://gitlab.freedesktop.org/libopenraw/exempi/issues/13
- https://gitlab.freedesktop.org/libopenraw/exempi/commit/fdd4765a699f9700850098b43b9798b933acb32f
