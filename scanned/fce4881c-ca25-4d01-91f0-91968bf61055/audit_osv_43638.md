# [H] dibs: fix use-after-free of dmb_node in loopback attach/detach/unregister

## Summary
Severity: High
Advisory: CVE-2026-74513
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74513
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dibs: fix use-after-free of dmb_node in loopback attach/detach/unregister

dibs_lo_attach_dmb(), dibs_lo_detach_dmb() and dibs_lo_unregister_dmb()
look up the dmb_node under dmb_ht_lock, drop the lock and only then
operate on the node's refcount. Nothing keeps the node alive across
that window: __dibs_lo_unregister_dmb() removes the node from the hash
table under the write lock and immediately frees it.

A concurrent final put can therefore free the node between the lookup
and the refcount operation:

CPU0 (attach)                     CPU1 (owner unregisters)

read_lock_bh(&dmb_ht_lock)
find dmb_node (refcnt == 1)
read_unlock_bh(&dmb_ht_lock)
                                  refcount_dec_and_test() 1 -> 0
                                  write_lock_bh(&dmb_ht_lock)
                                  hash_del(&dmb_node->list)
                                  write_unlock_bh(&dmb_ht_lock)
                                  kfree(dmb_node)
refcount_inc_not_zero(&dmb_node->refcnt)  <-- use-after-free

The same window exists for the refcount_dec_and_test() calls in the
detach and unregister paths.

Close the race structurally by making hash table membership and the
refcount transitions atomic with respect to each other:

- Perform the final refcount_dec_and_test() and hash_del() in a single
  dmb_ht_lock write-side critical section, in both the unregister and
  the detach path. Freeing the node still happens after the lock is
  dropped, which is safe because a node whose refcount reached zero has
  left the hash table and can no longer be found.

- This establishes the invariant that any node found in the hash table
  holds at least one reference, and that the final reference can only
  be dropped under the write lock. dibs_lo_attach_dmb() can thus take
  its reference with a plain refcount_inc() while still holding the
  read lock; refcount_inc_not_zero() is no longer needed.

__dibs_lo_unregister_dmb() no longer touches the hash table and is
renamed to dibs_lo_free_dmb() accordingly.

Note: commit cc21191b584c ("dibs: Move data path to dibs layer") moved
the code to its current location; the race was introduced earlier by
commit c3a910f2380f ("net/smc: implement DMB-merged operations of
loopback-ism").

Tested SMC-D via ISM and dibs loopback.

## References
- https://git.kernel.org/stable/c/48c073f88c93707089a4214f21cb4c3de5aea6e4
- https://git.kernel.org/stable/c/a10ea943356b9d70c5616a0a06f6fa97cfdaccb1
- https://git.kernel.org/stable/c/c0837aeace96152d14b17fdd19d70102b6631a7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74513.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74513
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
