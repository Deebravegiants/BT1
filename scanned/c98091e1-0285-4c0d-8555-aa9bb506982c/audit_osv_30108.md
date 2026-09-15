# [M] mm/damon/tests/sysfs-kunit.h: fix memory leak in damon_sysfs_test_add_targets()

## Summary
Severity: Medium
Advisory: CVE-2024-50068
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50068
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/damon/tests/sysfs-kunit.h: fix memory leak in damon_sysfs_test_add_targets()

The sysfs_target->regions allocated in damon_sysfs_regions_alloc() is not
freed in damon_sysfs_test_add_targets(), which cause the following memory
leak, free it to fix it.

	unreferenced object 0xffffff80c2a8db80 (size 96):
	  comm "kunit_try_catch", pid 187, jiffies 4294894363
	  hex dump (first 32 bytes):
	    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
	    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
	  backtrace (crc 0):
	    [<0000000001e3714d>] kmemleak_alloc+0x34/0x40
	    [<000000008e6835c1>] __kmalloc_cache_noprof+0x26c/0x2f4
	    [<000000001286d9f8>] damon_sysfs_test_add_targets+0x1cc/0x738
	    [<0000000032ef8f77>] kunit_try_run_case+0x13c/0x3ac
	    [<00000000f3edea23>] kunit_generic_run_threadfn_adapter+0x80/0xec
	    [<00000000adf936cf>] kthread+0x2e8/0x374
	    [<0000000041bb1628>] ret_from_fork+0x10/0x20

## References
- https://git.kernel.org/stable/c/05d43455f6bffa6abc7b937ca58be00452e6973f
- https://git.kernel.org/stable/c/2d6a1c835685de3b0c8e8dc871f60f4ef92ab01a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50068.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50068
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
