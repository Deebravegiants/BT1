# [M] iio: gts-helper: Fix memory leaks in iio_gts_build_avail_scale_table()

## Summary
Severity: Medium
Advisory: CVE-2024-50231
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50231
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: gts-helper: Fix memory leaks in iio_gts_build_avail_scale_table()

modprobe iio-test-gts and rmmod it, then the following memory leak
occurs:

	unreferenced object 0xffffff80c810be00 (size 64):
	  comm "kunit_try_catch", pid 1654, jiffies 4294913981
	  hex dump (first 32 bytes):
	    02 00 00 00 08 00 00 00 20 00 00 00 40 00 00 00  ........ ...@...
	    80 00 00 00 00 02 00 00 00 04 00 00 00 08 00 00  ................
	  backtrace (crc a63d875e):
	    [<0000000028c1b3c2>] kmemleak_alloc+0x34/0x40
	    [<000000001d6ecc87>] __kmalloc_noprof+0x2bc/0x3c0
	    [<00000000393795c1>] devm_iio_init_iio_gts+0x4b4/0x16f4
	    [<0000000071bb4b09>] 0xffffffdf052a62e0
	    [<000000000315bc18>] 0xffffffdf052a6488
	    [<00000000f9dc55b5>] kunit_try_run_case+0x13c/0x3ac
	    [<00000000175a3fd4>] kunit_generic_run_threadfn_adapter+0x80/0xec
	    [<00000000f505065d>] kthread+0x2e8/0x374
	    [<00000000bbfb0e5d>] ret_from_fork+0x10/0x20
	unreferenced object 0xffffff80cbfe9e70 (size 16):
	  comm "kunit_try_catch", pid 1658, jiffies 4294914015
	  hex dump (first 16 bytes):
	    10 00 00 00 40 00 00 00 80 00 00 00 00 00 00 00  ....@...........
	  backtrace (crc 857f0cb4):
	    [<0000000028c1b3c2>] kmemleak_alloc+0x34/0x40
	    [<000000001d6ecc87>] __kmalloc_noprof+0x2bc/0x3c0
	    [<00000000393795c1>] devm_iio_init_iio_gts+0x4b4/0x16f4
	    [<0000000071bb4b09>] 0xffffffdf052a62e0
	    [<000000007d089d45>] 0xffffffdf052a6864
	    [<00000000f9dc55b5>] kunit_try_run_case+0x13c/0x3ac
	    [<00000000175a3fd4>] kunit_generic_run_threadfn_adapter+0x80/0xec
	    [<00000000f505065d>] kthread+0x2e8/0x374
	    [<00000000bbfb0e5d>] ret_from_fork+0x10/0x20
	......

It includes 5*5 times "size 64" memory leaks, which correspond to 5 times
test_init_iio_gain_scale() calls with gts_test_gains size 10 (10*size(int))
and gts_test_itimes size 5. It also includes 5*1 times "size 16"
memory leak, which correspond to one time __test_init_iio_gain_scale()
call with gts_test_gains_gain_low size 3 (3*size(int)) and gts_test_itimes
size 5.

The reason is that the per_time_gains[i] is not freed which is allocated in
the "gts->num_itime" for loop in iio_gts_build_avail_scale_table().

## References
- https://git.kernel.org/stable/c/16e41593825c3044efca0eb34b2d6ffba306e4ec
- https://git.kernel.org/stable/c/38d6e8be234d87b0eedca50309e25051888b39d1
- https://git.kernel.org/stable/c/691e79ffc42154a9c91dc3b7e96a307037b4be74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50231.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50231
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
