# [H] mm: vmalloc: ensure vmap_block is initialised before adding to queue

## Summary
Severity: High
Advisory: CVE-2024-46847
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46847
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: vmalloc: ensure vmap_block is initialised before adding to queue

Commit 8c61291fd850 ("mm: fix incorrect vbq reference in
purge_fragmented_block") extended the 'vmap_block' structure to contain a
'cpu' field which is set at allocation time to the id of the initialising
CPU.

When a new 'vmap_block' is being instantiated by new_vmap_block(), the
partially initialised structure is added to the local 'vmap_block_queue'
xarray before the 'cpu' field has been initialised.  If another CPU is
concurrently walking the xarray (e.g.  via vm_unmap_aliases()), then it
may perform an out-of-bounds access to the remote queue thanks to an
uninitialised index.

This has been observed as UBSAN errors in Android:

 | Internal error: UBSAN: array index out of bounds: 00000000f2005512 [#1] PREEMPT SMP
 |
 | Call trace:
 |  purge_fragmented_block+0x204/0x21c
 |  _vm_unmap_aliases+0x170/0x378
 |  vm_unmap_aliases+0x1c/0x28
 |  change_memory_common+0x1dc/0x26c
 |  set_memory_ro+0x18/0x24
 |  module_enable_ro+0x98/0x238
 |  do_init_module+0x1b0/0x310

Move the initialisation of 'vb->cpu' in new_vmap_block() ahead of the
addition to the xarray.

## References
- https://git.kernel.org/stable/c/1b2770e27d6d952f491bb362b657e5b2713c3efd
- https://git.kernel.org/stable/c/3e3de7947c751509027d26b679ecd243bc9db255
- https://git.kernel.org/stable/c/6cf74e0e5e3ab5d5c9defb4c73dad54d52224671
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46847.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
