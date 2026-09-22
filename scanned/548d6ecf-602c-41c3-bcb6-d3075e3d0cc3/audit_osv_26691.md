# [H] ring-buffer: Sync IRQ works before buffer destruction

## Summary
Severity: High
Advisory: CVE-2023-53587
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53587
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Sync IRQ works before buffer destruction

If something was written to the buffer just before destruction,
it may be possible (maybe not in a real system, but it did
happen in ARCH=um with time-travel) to destroy the ringbuffer
before the IRQ work ran, leading this KASAN report (or a crash
without KASAN):

    BUG: KASAN: slab-use-after-free in irq_work_run_list+0x11a/0x13a
    Read of size 8 at addr 000000006d640a48 by task swapper/0

    CPU: 0 PID: 0 Comm: swapper Tainted: G        W  O       6.3.0-rc1 #7
    Stack:
     60c4f20f 0c203d48 41b58ab3 60f224fc
     600477fa 60f35687 60c4f20f 601273dd
     00000008 6101eb00 6101eab0 615be548
    Call Trace:
     [<60047a58>] show_stack+0x25e/0x282
     [<60c609e0>] dump_stack_lvl+0x96/0xfd
     [<60c50d4c>] print_report+0x1a7/0x5a8
     [<603078d3>] kasan_report+0xc1/0xe9
     [<60308950>] __asan_report_load8_noabort+0x1b/0x1d
     [<60232844>] irq_work_run_list+0x11a/0x13a
     [<602328b4>] irq_work_tick+0x24/0x34
     [<6017f9dc>] update_process_times+0x162/0x196
     [<6019f335>] tick_sched_handle+0x1a4/0x1c3
     [<6019fd9e>] tick_sched_timer+0x79/0x10c
     [<601812b9>] __hrtimer_run_queues.constprop.0+0x425/0x695
     [<60182913>] hrtimer_interrupt+0x16c/0x2c4
     [<600486a3>] um_timer+0x164/0x183
     [...]

    Allocated by task 411:
     save_stack_trace+0x99/0xb5
     stack_trace_save+0x81/0x9b
     kasan_save_stack+0x2d/0x54
     kasan_set_track+0x34/0x3e
     kasan_save_alloc_info+0x25/0x28
     ____kasan_kmalloc+0x8b/0x97
     __kasan_kmalloc+0x10/0x12
     __kmalloc+0xb2/0xe8
     load_elf_phdrs+0xee/0x182
     [...]

    The buggy address belongs to the object at 000000006d640800
     which belongs to the cache kmalloc-1k of size 1024
    The buggy address is located 584 bytes inside of
     freed 1024-byte region [000000006d640800, 000000006d640c00)

Add the appropriate irq_work_sync() so the work finishes before
the buffers are destroyed.

Prior to the commit in the Fixes tag below, there was only a
single global IRQ work, so this issue didn't exist.

## References
- https://git.kernel.org/stable/c/0a65165bd24ee9231191597b7c232376fcd70cdb
- https://git.kernel.org/stable/c/1c99f65d6af2a454bfd5207b4f6a97c8474a1191
- https://git.kernel.org/stable/c/2399b1fda025e939b6fb1ac94505bcf718534e65
- https://git.kernel.org/stable/c/2702b67f59d455072a08dc40312f9b090d4dec04
- https://git.kernel.org/stable/c/372c5ee537b8366b64b691ba29e9335525e1655e
- https://git.kernel.org/stable/c/675751bb20634f981498c7d66161584080cc061e
- https://git.kernel.org/stable/c/c63741e872fcfb10e153517750f7908f0c00f60d
- https://git.kernel.org/stable/c/d9834abd8b24d1fe8092859e436fe1e0fd467c61
- https://git.kernel.org/stable/c/fc6858b7f8e1221f62ce8c6ff8a13a349c32cd76
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53587.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53587
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
