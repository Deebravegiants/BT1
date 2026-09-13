# [H] crypto: amlogic - avoid double cleanup in meson_crypto_probe()

## Summary
Severity: High
Advisory: CVE-2026-64599
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64599
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: amlogic - avoid double cleanup in meson_crypto_probe()

When meson_allocate_chanlist() fails after a partial allocation, it already
unwinds the allocated chanlist state through its local error path.
meson_crypto_probe() then jump to error_flow and calls
meson_free_chanlist() again, causing the same per-flow resources to be torn
down twice. In the reproduced failure path, the second teardown
re-entered crypto_engine_exit() on an already destroyed worker and KASAN
reported a slab-use-after-free in kthread_destroy_worker().

Prevent double-free by handling partial allocation failures locally within
meson_allocate_chanlist() and skipping the outer cleanup path.

The bug was first flagged by an experimental analysis tool we are
developing for kernel memory-management bugs while analyzing
v6.13-rc1. The tool is still under development and is not yet publicly
available.

The bug was reproduced in a QEMU x86_64 guest booted with KASAN on v7.1,
using the reproducer under tools/testing/meson_crypto_probe. The reproducer
forces the second dma_alloc_attrs() call in the gxl-crypto probe path to
return NULL, making meson_allocate_chanlist() fail after partial
initialization. On the unpatched kernel this reliably triggered a
slab-use-after-free. With this fix applied, the same reproducer no longer
emits any KASAN report and the probe fails cleanly with -ENOMEM.

    ==================================================================
    BUG: KASAN: slab-use-after-free in kthread_destroy_worker+0xb2/0xd0
    Read of size 8 at addr ff1100010c057a68 by task insmod/265

    CPU: 1 UID: 0 PID: 265 Comm: insmod Tainted: G           O        7.1.0-rc2-00376-g810af9adc907-dirty #10 PREEMPT(lazy)
    Tainted: [O]=OOT_MODULE
    Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.15.0-1 04/01/2014
    Call Trace:
     <TASK>
     dump_stack_lvl+0x68/0xa0
     print_report+0xcb/0x5e0
     ? __virt_addr_valid+0x21d/0x3f0
     ? kthread_destroy_worker+0xb2/0xd0
     ? kthread_destroy_worker+0xb2/0xd0
     kasan_report+0xca/0x100
     ? kthread_destroy_worker+0xb2/0xd0
     kthread_destroy_worker+0xb2/0xd0
     meson_crypto_probe+0x4d0/0xc10 [amlogic_gxl_crypto]
     platform_probe+0x99/0x140
     really_probe+0x1c6/0x6a0
     ? __pfx___device_attach_driver+0x10/0x10
     __driver_probe_device+0x248/0x310
     ? acpi_driver_match_device+0xb0/0x100
     driver_probe_device+0x48/0x210
     ? __pfx___device_attach_driver+0x10/0x10
     __device_attach_driver+0x160/0x320
     bus_for_each_drv+0x104/0x190
     ? __pfx_bus_for_each_drv+0x10/0x10
     ? _raw_spin_unlock_irqrestore+0x2c/0x50
     __device_attach+0x19d/0x3b0
     ? __pfx___device_attach+0x10/0x10
     ? do_raw_spin_unlock+0x53/0x220
     device_initial_probe+0x78/0xa0
     bus_probe_device+0x5b/0x130
     device_add+0xcfd/0x1430
     ? __pfx_device_add+0x10/0x10
     ? insert_resource+0x34/0x50
     ? lock_release+0xc9/0x290
     platform_device_add+0x24e/0x590
     ? __pfx_meson_crypto_probe_repro_init+0x10/0x10 [meson_crypto_probe_repro]
     meson_crypto_probe_repro_init+0x330/0xff0 [meson_crypto_probe_repro]
     do_one_initcall+0xc0/0x450
     ? __pfx_do_one_initcall+0x10/0x10
     ? _raw_spin_unlock_irqrestore+0x2c/0x50
     ? __create_object+0x59/0x80
     ? kasan_unpoison+0x27/0x60
     do_init_module+0x27b/0x7d0
     ? __pfx_do_init_module+0x10/0x10
     ? kasan_quarantine_put+0x84/0x1d0
     ? kfree+0x32c/0x510
     ? load_module+0x561e/0x5ff0
     load_module+0x54fe/0x5ff0
     ? __pfx_load_module+0x10/0x10
     ? security_file_permission+0x20/0x40
     ? kernel_read_file+0x23d/0x6e0
     ? mmap_region+0x235/0x4a0
     ? __pfx_kernel_read_file+0x10/0x10
     ? __file_has_perm+0x2c0/0x3e0
     init_module_from_file+0x158/0x180
     ? __pfx_init_module_from_file+0x10/0x10
     ? __lock_acquire+0x45a/0x1ba0
     ? idempotent_init_module+0x315/0x610
     ? lock_release+0xc9/0x290
     ? lock
---truncated---

## References
- https://git.kernel.org/stable/c/5b452019a4127f63c1f2147237fc287d1581f606
- https://git.kernel.org/stable/c/6d827ade51a24e18d81afb9f32756d339520a14c
- https://git.kernel.org/stable/c/6dda8406d8a3da2519c8b388d443d7357839cb63
- https://git.kernel.org/stable/c/6effdbaca3cd8354540bdf42c7f5fb84412afeb7
- https://git.kernel.org/stable/c/84a00be9b736aa5dce902a290f62cbbbdcfab9ed
- https://git.kernel.org/stable/c/c2c48aa7a6be36d4c93da75d14d4b4f2f4168c81
- https://git.kernel.org/stable/c/c80360b4e85099fc3835378a96a59c0a2480fb07
- https://git.kernel.org/stable/c/f30e2b879bda14bc3e1524fba6f8ab9ec119da90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64599.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64599
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
