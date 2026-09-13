# [H] CVE-2021-46959

## Summary
Severity: High
Advisory: CVE-2021-46959
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-46959
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: Fix use-after-free with devm_spi_alloc_*

We can't rely on the contents of the devres list during
spi_unregister_controller(), as the list is already torn down at the
time we perform devres_find() for devm_spi_release_controller. This
causes devices registered with devm_spi_alloc_{master,slave}() to be
mistakenly identified as legacy, non-devm managed devices and have their
reference counters decremented below 0.

------------[ cut here ]------------
WARNING: CPU: 1 PID: 660 at lib/refcount.c:28 refcount_warn_saturate+0x108/0x174
[<b0396f04>] (refcount_warn_saturate) from [<b03c56a4>] (kobject_put+0x90/0x98)
[<b03c5614>] (kobject_put) from [<b0447b4c>] (put_device+0x20/0x24)
 r4:b6700140
[<b0447b2c>] (put_device) from [<b07515e8>] (devm_spi_release_controller+0x3c/0x40)
[<b07515ac>] (devm_spi_release_controller) from [<b045343c>] (release_nodes+0x84/0xc4)
 r5:b6700180 r4:b6700100
[<b04533b8>] (release_nodes) from [<b0454160>] (devres_release_all+0x5c/0x60)
 r8:b1638c54 r7:b117ad94 r6:b1638c10 r5:b117ad94 r4:b163dc10
[<b0454104>] (devres_release_all) from [<b044e41c>] (__device_release_driver+0x144/0x1ec)
 r5:b117ad94 r4:b163dc10
[<b044e2d8>] (__device_release_driver) from [<b044f70c>] (device_driver_detach+0x84/0xa0)
 r9:00000000 r8:00000000 r7:b117ad94 r6:b163dc54 r5:b1638c10 r4:b163dc10
[<b044f688>] (device_driver_detach) from [<b044d274>] (unbind_store+0xe4/0xf8)

Instead, determine the devm allocation state as a flag on the
controller which is guaranteed to be stable during cleanup.

## References
- https://git.kernel.org/stable/c/28a5529068c51cdf0295ab1e11a99a3a909a03e4
- https://git.kernel.org/stable/c/794aaf01444d4e765e2b067cba01cc69c1c68ed9
- https://git.kernel.org/stable/c/8bf96425c90f5c1dcf3b7b9df568019a1d4b8a0e
- https://git.kernel.org/stable/c/c7fabe372a9031acd00498bc718ce27c253abfd1
- https://git.kernel.org/stable/c/cee78aa24578edac8cf00513dca618c0acc17cd7
- https://git.kernel.org/stable/c/001c8e83646ad3b847b18f6ac55a54367d917d74
- https://git.kernel.org/stable/c/62bb2c7f2411a0045c24831f11ecacfc35610815
- https://git.kernel.org/stable/c/8735248ebb918d25427965f0db07939ed0473ec6
- https://git.kernel.org/stable/c/8e029707f50a82c53172359c686b2536ab54e58c
