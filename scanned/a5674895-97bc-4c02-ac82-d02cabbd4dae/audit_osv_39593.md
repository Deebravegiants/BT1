# [H] eventpoll: fix ep_remove struct eventpoll / struct file UAF

## Summary
Severity: High
Advisory: CVE-2026-46242
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-30
Source: https://osv.dev/vulnerability/CVE-2026-46242
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.178, >=6.2.0 <6.6.144, >=6.4.0 <6.12.95, >=6.7.0 <6.18.33, >=6.13.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

eventpoll: fix ep_remove struct eventpoll / struct file UAF

ep_remove() (via ep_remove_file()) cleared file->f_ep under
file->f_lock but then kept using @file inside the critical section
(is_file_epoll(), hlist_del_rcu() through the head, spin_unlock).
A concurrent __fput() taking the eventpoll_release() fastpath in
that window observed the transient NULL, skipped
eventpoll_release_file() and ran to f_op->release / file_free().

For the epoll-watches-epoll case, f_op->release is
ep_eventpoll_release() -> ep_clear_and_put() -> ep_free(), which
kfree()s the watched struct eventpoll. Its embedded ->refs
hlist_head is exactly where epi->fllink.pprev points, so the
subsequent hlist_del_rcu()'s "*pprev = next" scribbles into freed
kmalloc-192 memory.

In addition, struct file is SLAB_TYPESAFE_BY_RCU, so the slot
backing @file could be recycled by alloc_empty_file() --
reinitializing f_lock and f_ep -- while ep_remove() is still
nominally inside that lock. The upshot is an attacker-controllable
kmem_cache_free() against the wrong slab cache.

Pin @file via epi_fget() at the top of ep_remove() and gate the
critical section on the pin succeeding. With the pin held @file
cannot reach refcount zero, which holds __fput() off and
transitively keeps the watched struct eventpoll alive across the
hlist_del_rcu() and the f_lock use, closing both UAFs.

If the pin fails @file has already reached refcount zero and its
__fput() is in flight. Because we bailed before clearing f_ep,
that path takes the eventpoll_release() slow path into
eventpoll_release_file() and blocks on ep->mtx until the waiter
side's ep_clear_and_put() drops it. The bailed epi's share of
ep->refcount stays intact, so the trailing ep_refcount_dec_and_test()
in ep_clear_and_put() cannot free the eventpoll out from under
eventpoll_release_file(); the orphaned epi is then cleaned up
there.

A successful pin also proves we are not racing
eventpoll_release_file() on this epi, so drop the now-redundant
re-check of epi->dying under f_lock. The cheap lockless
READ_ONCE(epi->dying) fast-path bailout stays.

## References
- http://www.openwall.com/lists/oss-security/2026/07/08/14
- https://git.kernel.org/stable/c/2de4db145b2992da496fea6c51f9839be678ae24
- https://git.kernel.org/stable/c/3e1144d2515d28e4312e663ea05eac203101491d
- https://git.kernel.org/stable/c/9324de74a3a59b9fde9b62ee45ebaa71458ba2e5
- https://git.kernel.org/stable/c/a6dc643c69311677c574a0f17a3f4d66a5f3744b
- https://git.kernel.org/stable/c/ced39b6a8062bac5c18a1c3df85634107eb8664a
- https://git.kernel.org/stable/c/ef4ca02e95363e78977ca04340d44fe3b4b2b81f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46242.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
