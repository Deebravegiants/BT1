# [H] ext4: fix e4b bitmap inconsistency reports

## Summary
Severity: High
Advisory: CVE-2026-45942
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45942
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <6.6.130, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix e4b bitmap inconsistency reports

A bitmap inconsistency issue was observed during stress tests under
mixed huge-page workloads. Ext4 reported multiple e4b bitmap check
failures like:

ext4_mb_complex_scan_group:2508: group 350, 8179 free clusters as
per group info. But got 8192 blocks

Analysis and experimentation confirmed that the issue is caused by a
race condition between page migration and bitmap modification. Although
this timing window is extremely narrow, it is still hit in practice:

folio_lock                        ext4_mb_load_buddy
__migrate_folio
  check ref count
  folio_mc_copy                     __filemap_get_folio
                                      folio_try_get(folio)
                                  ......
                                  mb_mark_used
                                  ext4_mb_unload_buddy
  __folio_migrate_mapping
    folio_ref_freeze
folio_unlock

The root cause of this issue is that the fast path of load_buddy only
increments the folio's reference count, which is insufficient to prevent
concurrent folio migration. We observed that the folio migration process
acquires the folio lock. Therefore, we can determine whether to take the
fast path in load_buddy by checking the lock status. If the folio is
locked, we opt for the slow path (which acquires the lock) to close this
concurrency window.

Additionally, this change addresses the following issues:

When the DOUBLE_CHECK macro is enabled to inspect bitmap-related
issues, the following error may be triggered:

corruption in group 324 at byte 784(6272): f in copy != ff on
disk/prealloc

Analysis reveals that this is a false positive. There is a specific race
window where the bitmap and the group descriptor become momentarily
inconsistent, leading to this error report:

ext4_mb_load_buddy                   ext4_mb_load_buddy
  __filemap_get_folio(create|lock)
    folio_lock
  ext4_mb_init_cache
    folio_mark_uptodate
                                     __filemap_get_folio(no lock)
                                     ......
                                     mb_mark_used
                                       mb_mark_used_double
  mb_cmp_bitmaps
                                       mb_set_bits(e4b->bd_bitmap)
  folio_unlock

The original logic assumed that since mb_cmp_bitmaps is called when the
bitmap is newly loaded from disk, the folio lock would be sufficient to
prevent concurrent access. However, this overlooks a specific race
condition: if another process attempts to load buddy and finds the folio
is already in an uptodate state, it will immediately begin using it without
holding folio lock.

## References
- https://git.kernel.org/stable/c/29a07d691d282faf38c33d4b61839b89399110f9
- https://git.kernel.org/stable/c/57e83bfbe1e412ac42daced2086f3c6f9a17bba0
- https://git.kernel.org/stable/c/bdc56a9c46b2a99c12313122b9352b619a2e719e
- https://git.kernel.org/stable/c/c05033cfc5c7699cd4df8d48cef94d01da755f24
- https://git.kernel.org/stable/c/f29709a7a3fc38f5015d850504762cdef0e151f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45942.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45942
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
