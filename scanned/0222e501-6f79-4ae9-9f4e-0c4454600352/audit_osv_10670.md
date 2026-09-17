# [M] CVE-2017-18183

## Summary
Severity: Medium
Advisory: CVE-2017-18183
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2017-18183
Type: osv

## Details
An issue was discovered in QPDF before 7.0.0. There is an infinite loop in the QPDFWriter::enqueueObject() function in libqpdf/QPDFWriter.cc.

## References
- https://usn.ubuntu.com/3638-1/
- https://github.com/qpdf/qpdf/issues/143
- https://github.com/qpdf/qpdf/commit/8249a26d69f72b9cda584c14cc3f12769985e481
