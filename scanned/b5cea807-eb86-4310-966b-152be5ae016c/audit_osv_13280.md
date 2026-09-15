# [M] CVE-2018-19060

## Summary
Severity: Medium
Advisory: CVE-2018-19060
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-19060
Type: osv

## Details
An issue was discovered in Poppler 0.71.0. There is a NULL pointer dereference in goo/GooString.h, will lead to denial of service, as demonstrated by utils/pdfdetach.cc not validating a filename of an embedded file before constructing a save path.

## References
- https://access.redhat.com/errata/RHSA-2019:2022
- https://usn.ubuntu.com/3837-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/660
