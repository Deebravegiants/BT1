# [M] ALPINE-CVE-2026-56406

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56406
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56406
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.2-r0

## Details
libexpat before 2.8.2 has an integer overflow in XML_ParseBuffer because it lacked a check that was present in XML_Parse.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56406
