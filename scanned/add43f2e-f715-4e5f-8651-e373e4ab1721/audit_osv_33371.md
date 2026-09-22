# [H] af_unix: Initialise scc_index in unix_add_edge().

## Summary
Severity: High
Advisory: CVE-2025-40214
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40214
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.10.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: Initialise scc_index in unix_add_edge().

Quang Le reported that the AF_UNIX GC could garbage-collect a
receive queue of an alive in-flight socket, with a nice repro.

The repro consists of three stages.

  1)
    1-a. Create a single cyclic reference with many sockets
    1-b. close() all sockets
    1-c. Trigger GC

  2)
    2-a. Pass sk-A to an embryo sk-B
    2-b. Pass sk-X to sk-X
    2-c. Trigger GC

  3)
    3-a. accept() the embryo sk-B
    3-b. Pass sk-B to sk-C
    3-c. close() the in-flight sk-A
    3-d. Trigger GC

As of 2-c, sk-A and sk-X are linked to unix_unvisited_vertices,
and unix_walk_scc() groups them into two different SCCs:

  unix_sk(sk-A)->vertex->scc_index = 2 (UNIX_VERTEX_INDEX_START)
  unix_sk(sk-X)->vertex->scc_index = 3

Once GC completes, unix_graph_grouped is set to true.
Also, unix_graph_maybe_cyclic is set to true due to sk-X's
cyclic self-reference, which makes close() trigger GC.

At 3-b, unix_add_edge() allocates unix_sk(sk-B)->vertex and
links it to unix_unvisited_vertices.

unix_update_graph() is called at 3-a. and 3-b., but neither
unix_graph_grouped nor unix_graph_maybe_cyclic is changed
because both sk-B's listener and sk-C are not in-flight.

3-c decrements sk-A's file refcnt to 1.

Since unix_graph_grouped is true at 3-d, unix_walk_scc_fast()
is finally called and iterates 3 sockets sk-A, sk-B, and sk-X:

  sk-A -> sk-B (-> sk-C)
  sk-X -> sk-X

This is totally fine.  All of them are not yet close()d and
should be grouped into different SCCs.

However, unix_vertex_dead() misjudges that sk-A and sk-B are
in the same SCC and sk-A is dead.

  unix_sk(sk-A)->scc_index == unix_sk(sk-B)->scc_index <-- Wrong!
  &&
  sk-A's file refcnt == unix_sk(sk-A)->vertex->out_degree
                                       ^-- 1 in-flight count for sk-B
  -> sk-A is dead !?

The problem is that unix_add_edge() does not initialise scc_index.

Stage 1) is used for heap spraying, making a newly allocated
vertex have vertex->scc_index == 2 (UNIX_VERTEX_INDEX_START)
set by unix_walk_scc() at 1-c.

Let's track the max SCC index from the previous unix_walk_scc()
call and assign the max + 1 to a new vertex's scc_index.

This way, we can continue to avoid Tarjan's algorithm while
preventing misjudgments.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/1aa7e40ee850c9053e769957ce6541173891204d
- https://git.kernel.org/stable/c/20003fbb9174121b27bd1da6ebe61542ac4c327d
- https://git.kernel.org/stable/c/4cd8d755c7d4f515dd9abf483316aca2f1b7b0f3
- https://git.kernel.org/stable/c/60e6489f8e3b086bd1130ad4450a2c112e863791
- https://git.kernel.org/stable/c/db81ad20fd8aef7cc7d536c52ee5ea4c1f979128
- https://mohandacherir.github.io/Qdiv7/posts/unix_new_gc/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40214.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40214
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
