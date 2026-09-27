# [M] CVE-2017-11624

## Summary
Severity: Medium
Advisory: CVE-2017-11624
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-11624
Type: osv

## Details
A stack-consumption vulnerability was found in libqpdf in QPDF 6.0.0, which allows attackers to cause a denial of service via a crafted file, related to the QPDFTokenizer::resolveLiteral function in QPDFTokenizer.cc after two consecutive calls to QPDFObjectHandle::parseInternal, aka an "infinite loop."

## References
- https://usn.ubuntu.com/3638-1/
- http://somevulnsofadlab.blogspot.jp/2017/07/qpdfan-infinite-loop-in-libqpdf.html
- https://github.com/qpdf/qpdf/issues/117
