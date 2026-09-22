# [M] CVE-2015-9252

## Summary
Severity: Medium
Advisory: CVE-2015-9252
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2015-9252
Type: osv

## Details
An issue was discovered in QPDF before 7.0.0. Endless recursion causes stack exhaustion in QPDFTokenizer::resolveLiteral() in QPDFTokenizer.cc, related to the QPDF::resolve function in QPDF.cc.

## References
- https://github.com/qpdf/qpdf/commit/701b518d5c56a1449825a3a37a716c58e05e1c3e
- https://github.com/qpdf/qpdf/issues/51
- https://github.com/qpdf/qpdf/commit/701b518d5c56a1449825a3a37a716c58e05e1c3e
- https://github.com/qpdf/qpdf/issues/51
- https://usn.ubuntu.com/3638-1/
