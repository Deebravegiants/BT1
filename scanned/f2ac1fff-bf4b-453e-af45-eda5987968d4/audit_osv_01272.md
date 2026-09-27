# [C] ALPINE-CVE-2018-8795

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-8795
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-8795
Type: osv

## Affected
- Alpine:v3.10: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.11: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.12: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.13: `rdesktop` — affected >=0 <1.8.6-r0
- Alpine:v3.14: `rdesktop` — affected >=0 <1.8.6-r0

## Details
rdesktop versions up to and including v1.8.3 contain an Integer Overflow that leads to a Heap-Based Buffer Overflow in function process_bitmap_updates() and results in a memory corruption and probably even a remote code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-8795
