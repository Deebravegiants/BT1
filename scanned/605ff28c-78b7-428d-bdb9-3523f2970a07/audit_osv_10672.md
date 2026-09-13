# [M] CVE-2017-18185

## Summary
Severity: Medium
Advisory: CVE-2017-18185
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2017-18185
Type: osv

## Details
An issue was discovered in QPDF before 7.0.0. There is a large heap-based out-of-bounds read in the Pl_Buffer::write function in Pl_Buffer.cc. It is caused by an integer overflow in the PNG filter.

## References
- https://usn.ubuntu.com/3638-1/
- https://github.com/qpdf/qpdf/issues/150
- https://github.com/qpdf/qpdf/commit/ec7d74a386c0b2f38990079c3b0d2a2b30be0e71
