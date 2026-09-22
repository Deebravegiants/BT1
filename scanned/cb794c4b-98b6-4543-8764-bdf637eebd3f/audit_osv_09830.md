# [M] CVE-2017-11625

## Summary
Severity: Medium
Advisory: CVE-2017-11625
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/CVE-2017-11625
Type: osv

## Details
A stack-consumption vulnerability was found in libqpdf in QPDF 6.0.0, which allows attackers to cause a denial of service via a crafted file, related to the QPDF::resolveObjectsInStream function in QPDF.cc, aka an "infinite loop."

## References
- https://usn.ubuntu.com/3638-1/
- http://somevulnsofadlab.blogspot.jp/2017/07/qpdfan-infinite-loop-in-libqpdf_26.html
- https://github.com/qpdf/qpdf/issues/120
