# [M] ALPINE-CVE-2026-76641

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-76641
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-76641
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.4-r0

## Details
Expat through 2.8.3 contains an out-of-bounds read vulnerability that allows attackers to trigger memory corruption by processing XML with external entity parsers created via XML_ExternalEntityParserCreate. A struct size mismatch between ELEMENT_TYPE members causes storeAtts to read the attIndex member past allocated memory boundaries, resulting in failure to normalize whitespace in non-CDATA attributes or a wild pointer dereference causing a segfault. This vulnerability was introduced by the fix for CVE-2026-66046.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-76641
