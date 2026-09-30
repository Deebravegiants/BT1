# [H] net/sched: cls_u32: skip hash tables in u32_bind_class()

## Summary
Severity: High
Advisory: CVE-2026-74739
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74739
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: cls_u32: skip hash tables in u32_bind_class()

u32_walk() enumerates both struct tc_u_hnode and struct tc_u_knode
through the walker callback. u32_bind_class() unconditionally casts the
passed fh to tc_u_knode and accesses &n->res, so when fh is actually a
tc_u_hnode, which has no tcf_result member, this results in a
slab-out-of-bounds read of res->classid in tc_cls_bind_class().

The issue can be reproduced with the following commands:

    tc qdisc add dev lo root handle 1: hfsc
    tc class add dev lo parent 1: classid 1:1 hfsc sc rate 1000kbit
    tc filter add dev lo parent 1:1 protocol ip prio 1 u32 match u32 0 0 flowid 1:1
    tc class add dev lo parent 1: classid 1:2 hfsc sc rate 2000kbit

Fix this by skipping hash tables via the TC_U32_KEY(handle) check.

## References
- https://git.kernel.org/stable/c/19d114b93c94bdef70496f26685c2a6b242f41b3
- https://git.kernel.org/stable/c/31f26a95eeee926946809ac456c61a3217936a62
- https://git.kernel.org/stable/c/594a064d603202b9ee21e07679d854e5c1750cc4
- https://git.kernel.org/stable/c/6d3724e616faf952c3adcf8414fc21a828ef3709
- https://git.kernel.org/stable/c/e71f8e9ed6f311410b14741f6012afe01869c0fa
- https://git.kernel.org/stable/c/ec5f3005586a785689fd568361b0c5925cb1548b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74739.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74739
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
