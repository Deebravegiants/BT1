# [M] ALPINE-CVE-2026-31912

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-31912
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-31912
Type: osv

## Affected
- Alpine:v3.21: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.22: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.23: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.24: `libpcap` — affected >=0 <1.10.7-r0

## Details
libpcap BPF interpreter detects neither reaching the end of the filter program buffer due to lack of a return instruction nor executing a jump instruction with an offset that translates to a pointer outside of the buffer.  In particular uncommon use cases a crafted filter program can cause the interpreter to try reading the OS process memory in the 32GiB around the buffer on 64-bit architectures and in the entire address space on 32-bit architectures.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-31912
