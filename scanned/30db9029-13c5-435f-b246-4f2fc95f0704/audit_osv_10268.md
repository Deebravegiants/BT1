# [M] CVE-2017-14641

## Summary
Severity: Medium
Advisory: CVE-2017-14641
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14641
Type: osv

## Details
A NULL pointer dereference was discovered in the AP4_DataAtom class in MetaData/Ap4MetaData.cpp in Bento4 version 1.5.0-617. The vulnerability causes a segmentation fault and application crash, which leads to remote denial of service.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-null-pointer-dereference-in-ap4_dataatomap4_dataatom-ap4metadata-cpp/
- https://github.com/axiomatic-systems/Bento4/commit/41cad602709436628f07b4c4f64e9ff7a611f687
- https://github.com/axiomatic-systems/Bento4/issues/184
