# [M] CVE-2021-38115

## Summary
Severity: Medium
Advisory: CVE-2021-38115
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2021-38115
Type: osv

## Details
read_header_tga in gd_tga.c in the GD Graphics Library (aka LibGD) through 2.3.2 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted TGA file.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00003.html
- https://github.com/libgd/libgd/issues/697
- https://github.com/libgd/libgd/pull/711/commits/8b111b2b4a4842179be66db68d84dda91a246032
