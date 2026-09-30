# [H] ALPINE-CVE-2026-0799

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-0799
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-0799
Type: osv

## Affected
- Alpine:v3.21: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.22: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.23: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.24: `libpcap` — affected >=0 <1.10.7-r0

## Details
In BPF instructions that load/store a value from/to a scratch memory register the register index is an unsigned 32-bit integer and must not exceed 15, but libpcap BPF interpreter does not validate the value.  In particular uncommon use cases a crafted filter program can cause the interpreter to try reading and writing the OS process memory in the 16GiB starting at the current stack frame on 64-bit architectures and in the entire address space on 32-bit architectures.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-0799
