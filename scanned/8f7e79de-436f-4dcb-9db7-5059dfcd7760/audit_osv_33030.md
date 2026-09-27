# [H] bpf, arm64: Fix fp initialization for exception boundary

## Summary
Severity: High
Advisory: CVE-2025-38586
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38586
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, arm64: Fix fp initialization for exception boundary

In the ARM64 BPF JIT when prog->aux->exception_boundary is set for a BPF
program, find_used_callee_regs() is not called because for a program
acting as exception boundary, all callee saved registers are saved.
find_used_callee_regs() sets `ctx->fp_used = true;` when it sees FP
being used in any of the instructions.

For programs acting as exception boundary, ctx->fp_used remains false
even if frame pointer is used by the program and therefore, FP is not
set-up for such programs in the prologue. This can cause the kernel to
crash due to a pagefault.

Fix it by setting ctx->fp_used = true for exception boundary programs as
fp is always saved in such programs.

## References
- https://git.kernel.org/stable/c/0dbef493cae7d451f740558665893c000adb2321
- https://git.kernel.org/stable/c/1ce30231e0a2c8c361ee5f8f7f265fc17130adce
- https://git.kernel.org/stable/c/b114fcee766d5101eada1aca7bb5fd0a86c89b35
- https://git.kernel.org/stable/c/e23184725dbb72d5d02940222eee36dbba2aa422
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38586.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
