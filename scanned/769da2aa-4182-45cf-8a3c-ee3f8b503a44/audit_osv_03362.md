# [H] ALPINE-CVE-2025-6021

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-6021
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-6021
Type: osv

## Affected
- Alpine:v3.21: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.13.9-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.13.9-r0

## Details
A flaw was found in libxml2's xmlBuildQName function, where integer overflows in buffer size calculations can lead to a stack-based buffer overflow. This issue can result in memory corruption or a denial of service when processing crafted input.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-6021
