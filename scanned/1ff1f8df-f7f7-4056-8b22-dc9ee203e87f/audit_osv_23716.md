# [M] jffs2: fix memory leak in jffs2_do_fill_super

## Summary
Severity: Medium
Advisory: CVE-2022-49381
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49381
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

jffs2: fix memory leak in jffs2_do_fill_super

If jffs2_iget() or d_make_root() in jffs2_do_fill_super() returns
an error, we can observe the following kmemleak report:

--------------------------------------------
unreferenced object 0xffff888105a65340 (size 64):
  comm "mount", pid 710, jiffies 4302851558 (age 58.239s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<ffffffff859c45e5>] kmem_cache_alloc_trace+0x475/0x8a0
    [<ffffffff86160146>] jffs2_sum_init+0x96/0x1a0
    [<ffffffff86140e25>] jffs2_do_mount_fs+0x745/0x2120
    [<ffffffff86149fec>] jffs2_do_fill_super+0x35c/0x810
    [<ffffffff8614aae9>] jffs2_fill_super+0x2b9/0x3b0
    [...]
unreferenced object 0xffff8881bd7f0000 (size 65536):
  comm "mount", pid 710, jiffies 4302851558 (age 58.239s)
  hex dump (first 32 bytes):
    bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb  ................
    bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb  ................
  backtrace:
    [<ffffffff858579ba>] kmalloc_order+0xda/0x110
    [<ffffffff85857a11>] kmalloc_order_trace+0x21/0x130
    [<ffffffff859c2ed1>] __kmalloc+0x711/0x8a0
    [<ffffffff86160189>] jffs2_sum_init+0xd9/0x1a0
    [<ffffffff86140e25>] jffs2_do_mount_fs+0x745/0x2120
    [<ffffffff86149fec>] jffs2_do_fill_super+0x35c/0x810
    [<ffffffff8614aae9>] jffs2_fill_super+0x2b9/0x3b0
    [...]
--------------------------------------------

This is because the resources allocated in jffs2_sum_init() are not
released. Call jffs2_sum_exit() to release these resources to solve
the problem.

## References
- https://git.kernel.org/stable/c/28048a4cf3813b7cf5cc8cce629dfdc7951cb1c2
- https://git.kernel.org/stable/c/3252d327f977b14663a10967f3b0930d6c325687
- https://git.kernel.org/stable/c/4ba7bbeab8009faf3a726e565d98816593ddd5b0
- https://git.kernel.org/stable/c/4da8763a3d2b684c773b72ed80fad40bc264bc40
- https://git.kernel.org/stable/c/69295267c481545f636b69ff341b8db75aa136b9
- https://git.kernel.org/stable/c/c14adb1cf70a984ed081c67e9d27bc3caad9537c
- https://git.kernel.org/stable/c/cf9db013e167bc8fc2ecd7a13ed97a37df0c9dab
- https://git.kernel.org/stable/c/d3a4fff1e7e408c32649030daa7c2c42a7e19a95
- https://git.kernel.org/stable/c/ecc53e58596542791e82eff00702f8af7a313f70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49381.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49381
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
