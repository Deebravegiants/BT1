# [M] CVE-2018-19059

## Summary
Severity: Medium
Advisory: CVE-2018-19059
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-19059
Type: osv

## Details
An issue was discovered in Poppler 0.71.0. There is a out-of-bounds read in EmbFile::save2 in FileSpec.cc, will lead to denial of service, as demonstrated by utils/pdfdetach.cc not validating embedded files before save attempts.

## References
- https://access.redhat.com/errata/RHSA-2019:2022
- https://usn.ubuntu.com/3837-1/
- https://gitlab.freedesktop.org/poppler/poppler/issues/661
