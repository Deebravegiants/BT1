# [H] bpf: Fix array bounds error with may_goto

## Summary
Severity: High
Advisory: CVE-2025-22087
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22087
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix array bounds error with may_goto

may_goto uses an additional 8 bytes on the stack, which causes the
interpreters[] array to go out of bounds when calculating index by
stack_size.

1. If a BPF program is rewritten, re-evaluate the stack size. For non-JIT
cases, reject loading directly.

2. For non-JIT cases, calculating interpreters[idx] may still cause
out-of-bounds array access, and just warn about it.

3. For jit_requested cases, the execution of bpf_func also needs to be
warned. So move the definition of function __bpf_prog_ret0_warn out of
the macro definition CONFIG_BPF_JIT_ALWAYS_ON.

## References
- https://git.kernel.org/stable/c/19e6817f84000d0b06f09fd69ebd56217842c122
- https://git.kernel.org/stable/c/1a86ae57b2600e5749f5f674e9d4296ac00c69a8
- https://git.kernel.org/stable/c/4524b7febdd55fb99ae2e1f48db64019fa69e643
- https://git.kernel.org/stable/c/6ebc5030e0c5a698f1dd9a6684cddf6ccaed64a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22087.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
