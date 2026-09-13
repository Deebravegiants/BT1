# [H] CVE-2017-12595

## Summary
Severity: High
Advisory: CVE-2017-12595
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-27
Source: https://osv.dev/vulnerability/CVE-2017-12595
Type: osv

## Details
The tokenizer in QPDF 6.0.0 and 7.0.b1 is recursive for arrays and dictionaries, which allows remote attackers to cause a denial of service (stack consumption and segmentation fault) or possibly have unspecified other impact via a PDF document with a deep data structure, as demonstrated by a crash in QPDFObjectHandle::parseInternal in libqpdf/QPDFObjectHandle.cc.

## References
- https://usn.ubuntu.com/3638-1/
- https://github.com/qpdf/qpdf/commit/ad527a64f93dca12f6aabab2ca99ae5eb352ab4b
- https://github.com/qpdf/qpdf/issues/146
