# [C] CVE-2018-12578

## Summary
Severity: Critical
Advisory: CVE-2018-12578
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12578
Type: osv

## Details
There is a heap-based buffer overflow in bmp_compress1_row in appliers.cpp in sam2p 0.49.4 that leads to a denial of service or possibly unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00010.html
- https://github.com/pts/sam2p/issues/39
