# [H] af_unix: Unlink scc_entry in unix_del_edge().

## Summary
Severity: High
Advisory: CVE-2026-80521
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80521
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: Unlink scc_entry in unix_del_edge().

Kyle Zeng reported that GC could free a dead SCC partially.

The scenario is as follows:

   1) Create two SCCs:

       X -.   A <-> B
       ^--'

   2) Run the following concurrently:

      2-1) send() sk-B to sk-B from sk-X
      2-2) close() both A and B

At 2-1), there is a small window where unix_add_edges()
publishes a new edge (B <-> B) to GC but its skb is not queued
by skb_queue_tail().

If 2-2) completes before skb_queue_tail() and GC is triggered,
it judges A <-> B as dead, but B is not freed because GC cannot
collect the not-yet-queued skb holding the B <-> B edge.

       X -.   A <-> B -. This edge is visible
       ^--'         ^..'  but skb is not

This itself is not a problem since the next GC run will judge
B as dead as well and free it finally.

       X -.   A <.> B -.
       ^--'         ^--'

However, X's SCC forces the next GC to call unix_walk_scc_fast(),
and it iterates over A through B's scc_entry.

Let's unlink scc_entry before freeing the vertex in unix_del_edge().

## References
- https://git.kernel.org/stable/c/594d905195024b228c962627ae5ae7c17bd582a4
- https://git.kernel.org/stable/c/e3702470ced94fad74d71e2232f022d2eb752a6d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80521.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80521
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
