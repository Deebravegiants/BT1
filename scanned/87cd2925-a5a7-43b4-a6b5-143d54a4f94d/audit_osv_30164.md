# [M] LoongArch: Don't crash in stack_top() for tasks without vDSO

## Summary
Severity: Medium
Advisory: CVE-2024-50133
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50133
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: Don't crash in stack_top() for tasks without vDSO

Not all tasks have a vDSO mapped, for example kthreads never do. If such
a task ever ends up calling stack_top(), it will derefence the NULL vdso
pointer and crash.

This can for example happen when using kunit:

	[<9000000000203874>] stack_top+0x58/0xa8
	[<90000000002956cc>] arch_pick_mmap_layout+0x164/0x220
	[<90000000003c284c>] kunit_vm_mmap_init+0x108/0x12c
	[<90000000003c1fbc>] __kunit_add_resource+0x38/0x8c
	[<90000000003c2704>] kunit_vm_mmap+0x88/0xc8
	[<9000000000410b14>] usercopy_test_init+0xbc/0x25c
	[<90000000003c1db4>] kunit_try_run_case+0x5c/0x184
	[<90000000003c3d54>] kunit_generic_run_threadfn_adapter+0x24/0x48
	[<900000000022e4bc>] kthread+0xc8/0xd4
	[<9000000000200ce8>] ret_from_kernel_thread+0xc/0xa4

## References
- https://git.kernel.org/stable/c/041cc3860b06770357876d1114d615333b0fbf31
- https://git.kernel.org/stable/c/134475a9ab8487527238d270639a8cb74c10aab2
- https://git.kernel.org/stable/c/a67d4a02bf43e15544179895ede7d5f97b84b550
- https://git.kernel.org/stable/c/a94c197d4d749954dfaa37e907fcc8c04e4aad7e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50133.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
