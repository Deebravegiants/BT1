# [M] ALPINE-CVE-2026-31911

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-31911
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-31911
Type: osv

## Affected
- Alpine:v3.21: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.22: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.23: `libpcap` — affected >=0 <1.10.7-r0
- Alpine:v3.24: `libpcap` — affected >=0 <1.10.7-r0

## Details
libpcap BPF interpreter calls abort() if it encounters a BPF instruction that has an invalid opcode.  In particular uncommon use cases a crafted filter program can terminate the OS process.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-31911
