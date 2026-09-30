# [H] CVE-2018-25020

## Summary
Severity: High
Advisory: CVE-2018-25020
Aliases: A-210498909, PUB-A-210498909
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2018-25020
Type: osv

## Details
The BPF subsystem in the Linux kernel before 4.17 mishandles situations with a long jump over an instruction sequence where inner instructions require substantial expansions into multiple BPF instructions, leading to an overflow. This affects kernel/bpf/core.c and net/core/filter.c.

## References
- http://packetstormsecurity.com/files/165477/Kernel-Live-Patch-Security-Notice-LSN-0083-1.html
- https://security.netapp.com/advisory/ntap-20211229-0005/
- https://github.com/torvalds/linux/commit/050fad7c4534c13c8eb1d9c2ba66012e014773cb
