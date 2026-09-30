# [H] riscv: Fix register corruption from uninitialized cregs on error

## Summary
Severity: High
Advisory: CVE-2026-64082
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64082
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.187, >=6.2.0 <6.6.156, >=6.7.0 <6.12.108, >=6.13.0 <6.18.49, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: Fix register corruption from uninitialized cregs on error

compat_riscv_gpr_set() calls cregs_to_regs() unconditionally, even when
user_regset_copyin() fails. Since cregs is an uninitialized stack
variable, a copyin failure causes uninitialized stack data to be written
into the target task's pt_regs, corrupting its register state and
potentially leaking kernel stack contents.

compat_restore_sigcontext() has the same issue: it calls cregs_to_regs()
even when __copy_from_user() fails, leading to the same corruption of
the signal-returning task's register state on error.

Only call cregs_to_regs() when the user copy succeeds.

## References
- https://git.kernel.org/stable/c/0599aa23734c48de9bce36d043a9ec90c23945a1
- https://git.kernel.org/stable/c/2a7d1daf2674fe7d5b1cc99a4e3b5f0f72d5958f
- https://git.kernel.org/stable/c/66dedb6028c3df6c6a3372dd935b823917e150d5
- https://git.kernel.org/stable/c/6ebcbb53fc9bc30843054ed99fd60b8e542628f4
- https://git.kernel.org/stable/c/9e020156833f1ad0d425a1e3d85b65639f1c1c50
- https://git.kernel.org/stable/c/f2d88b0d7aebfa4643fc58bbae57210c6daff9c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64082.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64082
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
