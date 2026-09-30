# [H] ALPINE-CVE-2025-24855

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-24855
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-24855
Type: osv

## Affected
- Alpine:v3.18: `libxslt` — affected >=0 <1.1.38-r1
- Alpine:v3.19: `libxslt` — affected >=0 <1.1.39-r1
- Alpine:v3.20: `libxslt` — affected >=0 <1.1.39-r2
- Alpine:v3.21: `libxslt` — affected >=0 <1.1.42-r2
- Alpine:v3.22: `libxslt` — affected >=0 <1.1.43-r0
- Alpine:v3.23: `libxslt` — affected >=0 <1.1.43-r0
- Alpine:v3.24: `libxslt` — affected >=0 <1.1.43-r0

## Details
numbers.c in libxslt before 1.1.43 has a use-after-free because, in nested XPath evaluations, an XPath context node can be modified but never restored. This is related to xsltNumberFormatGetValue, xsltEvalXPathPredicate, xsltEvalXPathStringNs, and xsltComputeSortResultInternal.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-24855
