# [H] watch_queue: Fix filter limit check

## Summary
Severity: High
Advisory: CVE-2022-48847
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48847
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.106, >=5.11.0 <5.15.29, >=5.16.0 <5.16.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

watch_queue: Fix filter limit check

In watch_queue_set_filter(), there are a couple of places where we check
that the filter type value does not exceed what the type_filter bitmap
can hold.  One place calculates the number of bits by:

   if (tf[i].type >= sizeof(wfilter->type_filter) * 8)

which is fine, but the second does:

   if (tf[i].type >= sizeof(wfilter->type_filter) * BITS_PER_LONG)

which is not.  This can lead to a couple of out-of-bounds writes due to
a too-large type:

 (1) __set_bit() on wfilter->type_filter
 (2) Writing more elements in wfilter->filters[] than we allocated.

Fix this by just using the proper WATCH_TYPE__NR instead, which is the
number of types we actually know about.

The bug may cause an oops looking something like:

  BUG: KASAN: slab-out-of-bounds in watch_queue_set_filter+0x659/0x740
  Write of size 4 at addr ffff88800d2c66bc by task watch_queue_oob/611
  ...
  Call Trace:
   <TASK>
   dump_stack_lvl+0x45/0x59
   print_address_description.constprop.0+0x1f/0x150
   ...
   kasan_report.cold+0x7f/0x11b
   ...
   watch_queue_set_filter+0x659/0x740
   ...
   __x64_sys_ioctl+0x127/0x190
   do_syscall_64+0x43/0x90
   entry_SYSCALL_64_after_hwframe+0x44/0xae

  Allocated by task 611:
   kasan_save_stack+0x1e/0x40
   __kasan_kmalloc+0x81/0xa0
   watch_queue_set_filter+0x23a/0x740
   __x64_sys_ioctl+0x127/0x190
   do_syscall_64+0x43/0x90
   entry_SYSCALL_64_after_hwframe+0x44/0xae

  The buggy address belongs to the object at ffff88800d2c66a0
   which belongs to the cache kmalloc-32 of size 32
  The buggy address is located 28 bytes inside of
   32-byte region [ffff88800d2c66a0, ffff88800d2c66c0)

## References
- https://git.kernel.org/stable/c/1b09f28f70a5046acd64138075ae3f095238b045
- https://git.kernel.org/stable/c/648895da69ced90ca770fd941c3d9479a9d72c16
- https://git.kernel.org/stable/c/b36588ebbcef74583824c08352e75838d6fb4ff2
- https://git.kernel.org/stable/c/c993ee0f9f81caf5767a50d1faeba39a0dc82af2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48847.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
