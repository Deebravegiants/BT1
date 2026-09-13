# [H] ALPINE-CVE-2018-8897

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-8897
Ecosystem: Alpine:v3.10, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-8897
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.12: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.13: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.14: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.15: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.16: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.17: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.18: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.19: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.20: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.21: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.22: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.23: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.24: `xen` — affected >=0 <4.10.1-r1
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r5
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r9
- Alpine:v3.6: `xen` — affected >=0 <4.8.3-r1
- Alpine:v3.7: `xen` — affected >=0 <4.9.2-r2
- Alpine:v3.9: `xen` — affected >=0 <4.10.1-r1

## Details
A statement in the System Programming Guide of the Intel 64 and IA-32 Architectures Software Developer's Manual (SDM) was mishandled in the development of some or all operating-system kernels, resulting in unexpected behavior for #DB exceptions that are deferred by MOV SS or POP SS, as demonstrated by (for example) privilege escalation in Windows, macOS, some Xen configurations, or FreeBSD, or a Linux kernel crash. The MOV to SS and POP SS instructions inhibit interrupts (including NMIs), data breakpoints, and single step trap exceptions until the instruction boundary following the next instruction (SDM Vol. 3A; section 6.8.3). (The inhibited data breakpoints are those on memory accessed by the MOV to SS or POP to SS instruction itself.) Note that debug exceptions are not inhibited by the interrupt enable (EFLAGS.IF) system flag (SDM Vol. 3A; section 2.3). If the instruction following the MOV to SS or POP to SS instruction is an instruction like SYSCALL, SYSENTER, INT 3, etc. that transfers control to the operating system at CPL < 3, the debug exception is delivered after the transfer to CPL < 3 is complete. OS kernels may not expect this order of events and may therefore experience unexpected behavior when it occurs.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-8897
