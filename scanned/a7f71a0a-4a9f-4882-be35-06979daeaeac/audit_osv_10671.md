# [M] CVE-2017-18184

## Summary
Severity: Medium
Advisory: CVE-2017-18184
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2017-18184
Type: osv

## Details
An issue was discovered in QPDF before 7.0.0. There is a stack-based out-of-bounds read in the function iterate_rc4 in QPDF_encryption.cc.

## References
- https://usn.ubuntu.com/3638-1/
- https://github.com/qpdf/qpdf/issues/147
- https://github.com/qpdf/qpdf/commit/dea704f0ab7f625e1e7b3f9a1110b45b63157317
