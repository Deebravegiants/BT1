# [H] bpf: tcp: Fix use-after-free in bpf_iter_tcp_established_batch()

## Summary
Severity: High
Advisory: CVE-2026-74714
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74714
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: tcp: Fix use-after-free in bpf_iter_tcp_established_batch()

reqsk_queue_hash_req() publishes a TCP_NEW_SYN_RECV request_sock onto
the ehash chain, drops the bucket lock, and only afterwards sets
rsk_refcnt to 3.

Lockless readers such as __inet_lookup_established() handle this with
refcount_inc_not_zero(), but bpf_iter_tcp_established_batch() uses plain
sock_hold() while holding the bucket lock, on the assumption that the
lock guarantees sk_refcnt > 0. That assumption does not hold for
request_sock:

  CPU 0                                CPU 1
  -----                                -----
  tcp_conn_request()
   reqsk_queue_hash_req()
    inet_ehash_insert(req)
     spin_lock(bucket)
     __sk_nulls_add_node_rcu(req)      // rsk_refcnt == 0
     spin_unlock(bucket)
                                       bpf_iter_tcp_established_batch()
                                        spin_lock(bucket)
                                        sock_hold(req)   <-- addition on 0
                                        spin_unlock(bucket)
    refcount_set(&req->rsk_refcnt, 3)  // clobbers saturated value

which surfaces as:

  refcount_t: addition on 0; use-after-free.
  WARNING: lib/refcount.c:25 at refcount_warn_saturate+0x48/0x90, CPU#1
  Call Trace:
   bpf_iter_tcp_established_batch+0x14e/0x170
   bpf_iter_tcp_batch+0x53/0x200
   bpf_iter_tcp_seq_next+0x27/0x70
   bpf_seq_read+0x107/0x410
   vfs_read+0xb9/0x380

The iterator's stolen reference is lost when the publishing CPU's
refcount_set() overwrites the count, leaving the socket one reference
short. When the last legitimate owner drops its reference the reqsk is
freed while still reachable, leading to use-after-free.

This reproduces in seconds with tcp_syncookies=0, a handful of threads
doing connect()/close() to a local listener while others read an
iter/tcp link in a tight loop.

Use refcount_inc_not_zero() and skip the socket on failure. A skipped
socket is still part of the bucket, so keep counting it in expected.
The reallocations are sized from expected, and a request sock whose
refcount gets published while the lock is held across the last realloc
must already have room.

A skipped socket is counted in expected but never batched, so end_sk
can be short of expected on a batch that is actually complete. Decide
completeness by whether the walk left any socket behind instead. The
WARN after the locked realloc checks the same, replacing an
end_sk == expected check that could not hold on that path since
commit cdec67a489d4 ("bpf: tcp: Make sure iter->batch always
contains a full bucket snapshot").

If every matching socket in a bucket is mid-init (refcount 0), end_sk
stays 0. Advance to the next bucket rather than returning a batch entry
that was never filled this round.

## References
- https://git.kernel.org/stable/c/7d2b60a4bc0499f62ff8520af6309bbe170882fd
- https://git.kernel.org/stable/c/97e74d3e45d653c07c2d406fc530a9bbe3df8396
- https://git.kernel.org/stable/c/cc0295f89296ed351fc4b0b48fee887ba02c5d24
- https://git.kernel.org/stable/c/cefcbbe20846a45f9a7dae868f7ef1000953e2df
- https://git.kernel.org/stable/c/ddbe966b5d1fe212ada749bc3d0b410f1a7dea74
- https://git.kernel.org/stable/c/e5fd3f514e27db1f05fbd72ba615d74941e23c51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74714.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74714
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
