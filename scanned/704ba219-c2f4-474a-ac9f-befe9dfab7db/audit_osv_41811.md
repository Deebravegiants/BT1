# [H] l2tp: use refcount_inc_not_zero in l2tp_session_get_by_ifname

## Summary
Severity: High
Advisory: CVE-2026-63918
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63918
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

l2tp: use refcount_inc_not_zero in l2tp_session_get_by_ifname

A reader in l2tp_session_get_by_ifname() can return a pointer to a
session whose refcount has reached zero. The getter takes its
reference with plain refcount_inc(), but every other session getter
in the same file (l2tp_v2_session_get, l2tp_v3_session_get, and the
corresponding _get_next variants) uses refcount_inc_not_zero()
because the IDR/RCU lookup can race with refcount_dec_and_test() ->
l2tp_session_free() -> kfree_rcu(). The ifname getter is the only
outlier; the inconsistency was raised on-list after 979c017803c4
("l2tp: use list_del_rcu in l2tp_session_unhash").

A reader inside rcu_read_lock_bh() that matches session->ifname can
be preempted between the strcmp() and the refcount_inc(). If the
last reference drops on another CPU in that window, the reader's
refcount_inc() runs on a counter that has reached zero. refcount_t
catches the addition-on-zero, prints "refcount_t: addition on 0;
use-after-free", saturates the counter, and returns the saturated
pointer to the caller. Session memory is held live by the in-flight
RCU read section, but the kfree_rcu() callback queued from
l2tp_session_free() will free it once the grace period closes; a
caller that dereferences the returned session past that point hits
a slab-use-after-free. On PREEMPT_RT local_bh_disable() is a per-CPU
sleeping lock and the preemption window is real; on stock PREEMPT
kernels local_bh_disable() is a preempt_count increment that closes
the cross-CPU race in practice (see below).

Use refcount_inc_not_zero() and continue the list walk on failure,
matching the other session getters in the file. The ifname getter
is the only session getter in net/l2tp/ that still uses the bare
refcount_inc() pattern; this change restores file-internal
consistency. The success path is unchanged.

## References
- https://git.kernel.org/stable/c/05f95729ca844704d15e49ce14868af4b403b32b
- https://git.kernel.org/stable/c/782d60a6596aee9b29c2eecfa70033899278bf65
- https://git.kernel.org/stable/c/947013fd7c8c35dd5856557b215840098a3f67f8
- https://git.kernel.org/stable/c/ee80455feffb9cb62b5b58715cabeff495e666b2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63918.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63918
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
