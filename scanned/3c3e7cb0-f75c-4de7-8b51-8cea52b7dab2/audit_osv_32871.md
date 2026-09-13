# [H] sch_hfsc: make hfsc_qlen_notify() idempotent

## Summary
Severity: High
Advisory: CVE-2025-38177
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38177
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sch_hfsc: make hfsc_qlen_notify() idempotent

hfsc_qlen_notify() is not idempotent either and not friendly
to its callers, like fq_codel_dequeue(). Let's make it idempotent
to ease qdisc_tree_reduce_backlog() callers' life:

1. update_vf() decreases cl->cl_nactive, so we can check whether it is
non-zero before calling it.

2. eltree_remove() always removes RB node cl->el_node, but we can use
   RB_EMPTY_NODE() + RB_CLEAR_NODE() to make it safe.

## References
- https://git.kernel.org/stable/c/0475c85426b18eccdcb7f9fb58d8f8e9c6c58c87
- https://git.kernel.org/stable/c/51eb3b65544c9efd6a1026889ee5fb5aa62da3bb
- https://git.kernel.org/stable/c/72c61ffbeeb8c50f6d4d70c65d3283aa1bac57a7
- https://git.kernel.org/stable/c/9030a91235ae4845ec71902c3e0cecfc9ed1f2df
- https://git.kernel.org/stable/c/9a5fd5c2f4d4afdd5e405083ee53e0789ce76956
- https://git.kernel.org/stable/c/a5efc95a33bd4fcb879250852828cc58c7862970
- https://git.kernel.org/stable/c/c1175c4ad01dbc9c979d099861fa90a754f72059
- https://git.kernel.org/stable/c/d06476714d2819b550e0cc39222347e2c8941c9d
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38177.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38177
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
