# [H] drm/xe/reg_sr: Remove register pool

## Summary
Severity: High
Advisory: CVE-2024-56652
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56652
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/reg_sr: Remove register pool

That pool implementation doesn't really work: if the krealloc happens to
move the memory and return another address, the entries in the xarray
become invalid, leading to use-after-free later:

	BUG: KASAN: slab-use-after-free in xe_reg_sr_apply_mmio+0x570/0x760 [xe]
	Read of size 4 at addr ffff8881244b2590 by task modprobe/2753

	Allocated by task 2753:
	 kasan_save_stack+0x39/0x70
	 kasan_save_track+0x14/0x40
	 kasan_save_alloc_info+0x37/0x60
	 __kasan_kmalloc+0xc3/0xd0
	 __kmalloc_node_track_caller_noprof+0x200/0x6d0
	 krealloc_noprof+0x229/0x380

Simplify the code to fix the bug. A better pooling strategy may be added
back later if needed.

(cherry picked from commit e5283bd4dfecbd3335f43b62a68e24dae23f59e4)

## References
- https://git.kernel.org/stable/c/b0193a31a0ca5a0f9e60bb4a86537d46b98111b8
- https://git.kernel.org/stable/c/d7b028656c29b22fcde1c6ee1df5b28fbba987b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56652.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56652
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
