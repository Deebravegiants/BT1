# [M] CVE-2018-19777

## Summary
Severity: Medium
Advisory: CVE-2018-19777
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19777
Type: osv

## Details
In Artifex MuPDF 1.14.0, there is an infinite loop in the function svg_dev_end_tile in fitz/svg-device.c, as demonstrated by mutool.

## References
- http://www.ghostscript.com/cgi-bin/findgit.cgi?754ac68f119e0c25cd33c5d652d8aabd533a9fb3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VUXKCY35PKC32IFHN4RBUCZ75OWEYVJH/
- https://bugs.ghostscript.com/show_bug.cgi?id=700301
