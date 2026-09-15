# [C] ksmbd: close durable scavenger races against m_fp_list lookups

## Summary
Severity: Critical
Advisory: CVE-2026-64142
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64142
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: close durable scavenger races against m_fp_list lookups

ksmbd_durable_scavenger() has two related races against any walker
that iterates f_ci->m_fp_list, including ksmbd_lookup_fd_inode()
(used by ksmbd_vfs_rename) and the share-mode checks in
fs/smb/server/smb_common.c.

(1) fp->node list-head reuse.  Durable-preserved handles can remain
linked on f_ci->m_fp_list after session teardown so share-mode checks
still see them while the handle is reconnectable.  The scavenger
collected expired handles by adding fp->node to a local
scavenger_list after removing them from the global durable idr.
Because fp->node is the same list_head used by m_fp_list,
list_add(&fp->node, &scavenger_list) overwrites the m_fp_list links
and corrupts both lists.  CONFIG_DEBUG_LIST can report this on the
share-mode walk path.

(2) Refcount race against m_fp_list walkers.  The scavenger qualifies
an expired durable handle with atomic_read(&fp->refcount) > 1 and
fp->conn under global_ft.lock, removes fp from global_ft, then drops
global_ft.lock before unlinking fp from m_fp_list and freeing it.
During that gap fp is still linked on m_fp_list with f_state ==
FP_INITED.  ksmbd_lookup_fd_inode() under m_lock read calls
ksmbd_fp_get() (atomic_inc_not_zero on refcount that is still 1) and
takes a live reference; the scavenger then unlinks and frees fp
while the holder owns a reference, leading to UAF on the holder's
subsequent ksmbd_fd_put() and on any field reads performed by a
concurrent share-mode walker that iterates m_fp_list without taking
ksmbd_fp_get() (smb_check_perm_dleases-like paths).

Fix both:

  * Stop reusing fp->node as a scavenger-private list node.  Remove
    one expired handle from global_ft under global_ft.lock, take an
    explicit transient reference, drop the lock, unlink fp->node
    from m_fp_list under f_ci->m_lock, then drop both the durable
    lifetime and transient references with atomic_sub_and_test(2,
    &fp->refcount).  If the scavenger is the last putter the close
    runs there; otherwise an in-flight holder that already raced
    through the m_fp_list lookup owns the final close via its
    ksmbd_fd_put() path.  The one-at-a-time disposal can rescan the
    durable idr when multiple handles expire in the same pass, but
    durable scavenging is a background expiration path and the final
    full scan recomputes min_timeout before the next wait.

  * Clear fp->persistent_id inside __ksmbd_remove_durable_fd() right
    after idr_remove(), so a delayed final close from a holder that
    snatched fp does not re-issue idr_remove() on a persistent id
    that idr_alloc_cyclic() in ksmbd_open_durable_fd() may have
    already handed out to a brand-new durable handle.

  * Bypass the per-conn open_files_count decrement in
    __put_fd_final() when fp is detached from any session table
    (fp->conn cleared by session_fd_check() at durable preserve --
    paired with the volatile_id clear at unpublish, so checking
    fp->conn alone is sufficient).  The walker that owns the final
    close runs from an unrelated work->conn whose
    stats.open_files_count never tracked this durable fp; without
    this guard the holder would underflow that unrelated counter.

The two races are folded into one patch because patch (1) alone
cleans up the corrupted list but leaves a deterministic UAF window
for m_fp_list walkers that the transient-reference and
persistent_id discipline in (2) close; bisecting onto an
intermediate state would land on a UAF that pre-patch chaos merely
made less reproducible.

Validation:
  * CONFIG_DEBUG_LIST coverage for the list_head reuse path.
  * KASAN-enabled direct SMB2 durable-handle coverage that exercised
    ksmbd_durable_scavenger() and non-NULL ksmbd_lookup_fd_inode()
    returns while durable handles expired under concurrent rename
    lookups, with no KASAN, UAF, list-corruption, ODEBUG, or WARNING
    reports.
---truncated---

## References
- https://git.kernel.org/stable/c/1f8f3246d55f89350a1a67bdf3744b7241048e4e
- https://git.kernel.org/stable/c/3a436932eb397e909d0607d76a8325abd9d85a35
- https://git.kernel.org/stable/c/5da69a65b282d2276de22e5194ba0f88c836170c
- https://git.kernel.org/stable/c/95f072ef934ca00711d510676b8792cbf59a5aae
- https://git.kernel.org/stable/c/bf736184d063da1a552ffeff0481813599a182cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64142.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64142
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
