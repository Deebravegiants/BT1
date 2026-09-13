# [H] start_kernel: Add __no_stack_protector function attribute

## Summary
Severity: High
Advisory: CVE-2023-53491
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53491
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

start_kernel: Add __no_stack_protector function attribute

Back during the discussion of
commit a9a3ed1eff36 ("x86: Fix early boot crash on gcc-10, third try")
we discussed the need for a function attribute to control the omission
of stack protectors on a per-function basis; at the time Clang had
support for no_stack_protector but GCC did not. This was fixed in
gcc-11. Now that the function attribute is available, let's start using
it.

Callers of boot_init_stack_canary need to use this function attribute
unless they're compiled with -fno-stack-protector, otherwise the canary
stored in the stack slot of the caller will differ upon the call to
boot_init_stack_canary. This will lead to a call to __stack_chk_fail()
then panic.

## References
- https://git.kernel.org/stable/c/25e73018b4093e0cfbcec5dc4a4bb86d0b69ed56
- https://git.kernel.org/stable/c/514ca14ed5444b911de59ed3381dfd195d99fe4b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53491.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53491
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
