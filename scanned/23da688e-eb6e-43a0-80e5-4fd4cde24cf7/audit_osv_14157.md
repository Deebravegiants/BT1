# [C] CVE-2018-7552

## Summary
Severity: Critical
Advisory: CVE-2018-7552
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-28
Source: https://osv.dev/vulnerability/CVE-2018-7552
Type: osv

## Details
There is an invalid free in Mapping::DoubleHash::clear in mapping.cpp that leads to a Segmentation fault in sam2p 0.49.4. A crafted input will lead to a denial of service or possibly unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2018/04/msg00004.html
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=891527
- https://github.com/pts/sam2p/issues/30
