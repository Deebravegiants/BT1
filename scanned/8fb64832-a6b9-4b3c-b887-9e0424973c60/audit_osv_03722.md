# [H] ALPINE-CVE-2026-43618

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-43618
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43618
Type: osv

## Affected
- Alpine:v3.20: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.3-r0

## Details
Rsync version 3.4.2 and prior contain an integer overflow vulnerability in the compressed-token decoder where a 32-bit signed counter is not checked for overflow, allowing a malicious sender to trigger an overflow that causes the receiver process to read and return data from outside the intended buffer bounds. Attackers can exploit this vulnerability to disclose process memory contents including environment variables, passwords, heap and stack data, and library memory pointers, significantly reducing ASLR effectiveness and facilitating further exploitation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43618
