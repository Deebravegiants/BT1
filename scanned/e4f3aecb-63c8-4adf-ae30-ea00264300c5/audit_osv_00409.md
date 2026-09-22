# [M] ALPINE-CVE-2017-11624

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-11624
Ecosystem: Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11624
Type: osv

## Affected
- Alpine:v3.8: `qpdf` — affected >=0 <7.0.0-r0
- Alpine:v3.9: `qpdf` — affected >=0 <7.0.0-r0

## Details
A stack-consumption vulnerability was found in libqpdf in QPDF 6.0.0, which allows attackers to cause a denial of service via a crafted file, related to the QPDFTokenizer::resolveLiteral function in QPDFTokenizer.cc after two consecutive calls to QPDFObjectHandle::parseInternal, aka an "infinite loop."

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11624
