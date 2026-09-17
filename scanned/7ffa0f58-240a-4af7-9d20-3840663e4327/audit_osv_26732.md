# [H] arm64: sme: Use STR P to clear FFR context field in streaming SVE mode

## Summary
Severity: High
Advisory: CVE-2023-53713
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53713
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: sme: Use STR P to clear FFR context field in streaming SVE mode

The FFR is a predicate register which can vary between 16 and 256 bits
in size depending upon the configured vector length. When saving the
SVE state in streaming SVE mode, the FFR register is inaccessible and
so commit 9f5848665788 ("arm64/sve: Make access to FFR optional") simply
clears the FFR field of the in-memory context structure. Unfortunately,
it achieves this using an unconditional 8-byte store and so if the SME
vector length is anything other than 64 bytes in size we will either
fail to clear the entire field or, worse, we will corrupt memory
immediately following the structure. This has led to intermittent kfence
splats in CI [1] and can trigger kmalloc Redzone corruption messages
when running the 'fp-stress' kselftest:

 | =============================================================================
 | BUG kmalloc-1k (Not tainted): kmalloc Redzone overwritten
 | -----------------------------------------------------------------------------
 |
 | 0xffff000809bf1e22-0xffff000809bf1e27 @offset=7714. First byte 0x0 instead of 0xcc
 | Allocated in do_sme_acc+0x9c/0x220 age=2613 cpu=1 pid=531
 |  __kmalloc+0x8c/0xcc
 |  do_sme_acc+0x9c/0x220
 |  ...

Replace the 8-byte store with a store of a predicate register which has
been zero-initialised with PFALSE, ensuring that the entire field is
cleared in memory.

[1] https://lore.kernel.org/r/CA+G9fYtU7HsV0R0dp4XEH5xXHSJFw8KyDf5VQrLLfMxWfxQkag@mail.gmail.com

## References
- https://git.kernel.org/stable/c/1403a899153a12d93fd510e463fd6d0eafba4336
- https://git.kernel.org/stable/c/8769a62faacbbb6cac5e35d9047ce445183d4e9f
- https://git.kernel.org/stable/c/893b24181b4c4bf1fa2841b1ed192e5413a97cb1
- https://git.kernel.org/stable/c/97669214944e80d3756657c21c4f286f3da6a423
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53713.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53713
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
