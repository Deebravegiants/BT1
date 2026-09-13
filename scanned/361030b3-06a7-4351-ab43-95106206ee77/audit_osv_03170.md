# [H] ALPINE-CVE-2024-8176

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-8176
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-8176
Type: osv

## Affected
- Alpine:v3.18: `expat` — affected >=0 <2.7.0-r0
- Alpine:v3.19: `expat` — affected >=0 <2.7.0-r0
- Alpine:v3.20: `expat` — affected >=0 <2.7.0-r0
- Alpine:v3.21: `expat` — affected >=0 <2.7.0-r0
- Alpine:v3.22: `expat` — affected >=0 <2.7.0-r0
- Alpine:v3.23: `expat` — affected >=0 <2.7.0-r0
- Alpine:v3.24: `expat` — affected >=0 <2.7.0-r0

## Details
A stack overflow vulnerability exists in the libexpat library due to the way it handles recursive entity expansion in XML documents. When parsing an XML document with deeply nested entity references, libexpat can be forced to recurse indefinitely, exhausting the stack space and causing a crash. This issue could lead to denial of service (DoS) or, in some cases, exploitable memory corruption, depending on the environment and library usage.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-8176
