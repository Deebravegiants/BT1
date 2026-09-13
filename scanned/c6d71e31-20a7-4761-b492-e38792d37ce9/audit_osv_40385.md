# [H] bpf: Fix same-register dst/src OOB read and pointer leak in sock_ops

## Summary
Severity: High
Advisory: CVE-2026-53078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53078
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix same-register dst/src OOB read and pointer leak in sock_ops

When a BPF sock_ops program accesses ctx fields with dst_reg == src_reg,
the SOCK_OPS_GET_SK() and SOCK_OPS_GET_FIELD() macros fail to zero the
destination register in the !fullsock / !locked_tcp_sock path.

Both macros borrow a temporary register to check is_fullsock /
is_locked_tcp_sock when dst_reg == src_reg, because dst_reg holds the
ctx pointer. When the check is false (e.g., TCP_NEW_SYN_RECV state with
a request_sock), dst_reg should be zeroed but is not, leaving the stale
ctx pointer:

 - SOCK_OPS_GET_SK: dst_reg retains the ctx pointer, passes NULL checks
   as PTR_TO_SOCKET_OR_NULL, and can be used as a bogus socket pointer,
   leading to stack-out-of-bounds access in helpers like
   bpf_skc_to_tcp6_sock().

 - SOCK_OPS_GET_FIELD: dst_reg retains the ctx pointer which the
   verifier believes is a SCALAR_VALUE, leaking a kernel pointer.

Fix both macros by:
 - Changing JMP_A(1) to JMP_A(2) in the fullsock path to skip the
   added instruction.
 - Adding BPF_MOV64_IMM(si->dst_reg, 0) after the temp register
   restore in the !fullsock path, placed after the restore because
   dst_reg == src_reg means we need src_reg intact to read ctx->temp.

## References
- https://git.kernel.org/stable/c/10f86a2a5c91fc4c4d001960f1c21abe52545ef6
- https://git.kernel.org/stable/c/18e3ffde1822f0b48b1753bf34aa97ce839df1d8
- https://git.kernel.org/stable/c/22400725de070b787cd6d806c5795370ab46d269
- https://git.kernel.org/stable/c/2a2c98141e0a75f2d4a7d78b0316c88b3da784ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53078.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
