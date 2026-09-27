# [H] mm/slab: return NULL early from kmalloc_nolock() in NMI on UP

## Summary
Severity: High
Advisory: CVE-2026-46029
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46029
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/slab: return NULL early from kmalloc_nolock() in NMI on UP

On UP kernels (!CONFIG_SMP), spin_trylock() is a no-op that
unconditionally succeeds even when the lock is already held. As a
result, kmalloc_nolock() called from NMI context can re-enter the slab
allocator and acquire n->list_lock that the interrupted context is
already holding, corrupting slab state.

With CONFIG_DEBUG_SPINLOCK on UP, the following BUG is triggered with
the slub_kunit test module:

  BUG: spinlock trylock failure on UP on CPU#0, kunit_try_catch/243
  [...]
  Call Trace:
   <NMI>
   dump_stack_lvl+0x3f/0x60
   do_raw_spin_trylock+0x41/0x50
   _raw_spin_trylock+0x24/0x50
   get_from_partial_node+0x120/0x4d0
   ___slab_alloc+0x8a/0x4c0
   kmalloc_nolock_noprof+0x164/0x310
   [...]
   </NMI>

Fix this by returning NULL early when invoked from NMI on a UP kernel.

## References
- https://git.kernel.org/stable/c/5b31044e649e3e54c2caef135c09b371c2fbcd08
- https://git.kernel.org/stable/c/a8d95d274be241ad21f6523bf2d6ba0d7d7e46b7
- https://git.kernel.org/stable/c/d66553204a15bdb257d9ef8aca1e12f5fbb910b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46029.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46029
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
