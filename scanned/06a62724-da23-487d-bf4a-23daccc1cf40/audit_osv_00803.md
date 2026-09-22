# [M] ALPINE-CVE-2017-9209

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-9209
Ecosystem: Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9209
Type: osv

## Affected
- Alpine:v3.8: `qpdf` — affected >=0 <7.0.0-r0
- Alpine:v3.9: `qpdf` — affected >=0 <7.0.0-r0

## Details
libqpdf.a in QPDF 6.0.0 allows remote attackers to cause a denial of service (infinite recursion and stack consumption) via a crafted PDF document, related to QPDFObjectHandle::parseInternal, aka qpdf-infiniteloop2.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9209
