# [M] jffs2: fix memory leak in jffs2_do_mount_fs

## Summary
Severity: Medium
Advisory: CVE-2022-49277
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49277
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <4.9.311, >=4.10.0 <4.14.276, >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

jffs2: fix memory leak in jffs2_do_mount_fs

If jffs2_build_filesystem() in jffs2_do_mount_fs() returns an error,
we can observe the following kmemleak report:

--------------------------------------------
unreferenced object 0xffff88811b25a640 (size 64):
  comm "mount", pid 691, jiffies 4294957728 (age 71.952s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<ffffffffa493be24>] kmem_cache_alloc_trace+0x584/0x880
    [<ffffffffa5423a06>] jffs2_sum_init+0x86/0x130
    [<ffffffffa5400e58>] jffs2_do_mount_fs+0x798/0xac0
    [<ffffffffa540acf3>] jffs2_do_fill_super+0x383/0xc30
    [<ffffffffa540c00a>] jffs2_fill_super+0x2ea/0x4c0
    [...]
unreferenced object 0xffff88812c760000 (size 65536):
  comm "mount", pid 691, jiffies 4294957728 (age 71.952s)
  hex dump (first 32 bytes):
    bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb  ................
    bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb  ................
  backtrace:
    [<ffffffffa493a449>] __kmalloc+0x6b9/0x910
    [<ffffffffa5423a57>] jffs2_sum_init+0xd7/0x130
    [<ffffffffa5400e58>] jffs2_do_mount_fs+0x798/0xac0
    [<ffffffffa540acf3>] jffs2_do_fill_super+0x383/0xc30
    [<ffffffffa540c00a>] jffs2_fill_super+0x2ea/0x4c0
    [...]
--------------------------------------------

This is because the resources allocated in jffs2_sum_init() are not
released. Call jffs2_sum_exit() to release these resources to solve
the problem.

## References
- https://git.kernel.org/stable/c/0978e9af4559a171ac7a74a1b3ef21804b0a0fa9
- https://git.kernel.org/stable/c/2a9d8184458562e6bf2f40d0e677fc85e2dd3834
- https://git.kernel.org/stable/c/4392e8aeebc5a4f8073620bccba7de1b1f6d7c88
- https://git.kernel.org/stable/c/5f34310d1376ca5b2ed798258def2c2ab3cc6699
- https://git.kernel.org/stable/c/607d3aab7349f18e0d9dba4100d09d16fe27caca
- https://git.kernel.org/stable/c/9a0f6610c7daedd2eace430beeb08a8b7ac80699
- https://git.kernel.org/stable/c/c94128470e6fe53d9bd9d16d2d3271813f9d37af
- https://git.kernel.org/stable/c/d051cef784de4d54835f6b6836d98a8f6935772c
- https://git.kernel.org/stable/c/dbe0d0521eaa6a3d235517319266c539bb5c5112
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49277.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
