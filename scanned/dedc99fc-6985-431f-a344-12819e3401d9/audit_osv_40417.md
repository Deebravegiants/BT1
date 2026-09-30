# [C] inet: frags: fix use-after-free caused by the fqdir_pre_exit() flush

## Summary
Severity: Critical
Advisory: CVE-2026-53175
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53175
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

inet: frags: fix use-after-free caused by the fqdir_pre_exit() flush

On netns teardown, fqdir_pre_exit() walks the fqdir rhashtable and
flushes every fragment queue that is not yet complete using
inet_frag_queue_flush(). That helper frees all the skbs queued on the
fragment queue but does not set INET_FRAG_COMPLETE, and leaves
q->fragments_tail and q->last_run_head pointing at the freed skbs.
The queue itself stays in the rhashtable.

fqdir_pre_exit() first lowers high_thresh to 0 to stop new queue lookups,
but it cannot stop a fragment that already obtained the queue through
inet_frag_find() earlier and stalled just before taking the queue lock.
Once that fragment resumes after the flush and takes the queue lock,
it passes the INET_FRAG_COMPLETE check and then dereferences the freed
fragments_tail. inet_frag_queue_insert() reads FRAG_CB() and ->len of
that pointer and, on the append path, writes ->next_frag, causing a
slab use-after-free. IPv6, nf_conntrack_reasm6 and 6lowpan reassembly
share the same flush path and are affected as well.

Reset rb_fragments, fragments_tail and last_run_head in
inet_frag_queue_flush() so a flushed queue no longer points at the
freed skbs. A fragment that resumes after the flush and takes the
queue lock then finds an empty queue and starts a new run instead of
dereferencing the freed fragments_tail. ip_frag_reinit() already
performed this reset after its own flush, so drop the now duplicate
code there.

## References
- https://git.kernel.org/stable/c/010c3313a4d178dc2d3ce958d2e5cb055e2864c1
- https://git.kernel.org/stable/c/0e823ca0e7391630784ae7dd0981b7ad170a93d9
- https://git.kernel.org/stable/c/32594b09854970d7ba83eb2dc8c69a2edd158c8e
- https://git.kernel.org/stable/c/89b909e9704587bfecc1aab1d37e98faee03b9f9
- https://git.kernel.org/stable/c/c22599cc90e1cd5f8129c8670bd68a02ff7177b4
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53175.json
- https://access.redhat.com/security/cve/CVE-2026-53175
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53175.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53175
- https://bugzilla.redhat.com/show_bug.cgi?id=2492840
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
