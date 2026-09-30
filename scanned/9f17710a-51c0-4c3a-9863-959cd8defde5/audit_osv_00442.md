# [H] ALPINE-CVE-2017-12595

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12595
Ecosystem: Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12595
Type: osv

## Affected
- Alpine:v3.8: `qpdf` — affected >=0 <7.0.0-r0
- Alpine:v3.9: `qpdf` — affected >=0 <7.0.0-r0

## Details
The tokenizer in QPDF 6.0.0 and 7.0.b1 is recursive for arrays and dictionaries, which allows remote attackers to cause a denial of service (stack consumption and segmentation fault) or possibly have unspecified other impact via a PDF document with a deep data structure, as demonstrated by a crash in QPDFObjectHandle::parseInternal in libqpdf/QPDFObjectHandle.cc.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12595
