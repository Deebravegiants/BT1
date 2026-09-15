# [H] netfilter: nf_tables: unconditionally flush pending work before notifier

## Summary
Severity: High
Advisory: CVE-2024-42109
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42109
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.5.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: unconditionally flush pending work before notifier

syzbot reports:

KASAN: slab-uaf in nft_ctx_update include/net/netfilter/nf_tables.h:1831
KASAN: slab-uaf in nft_commit_release net/netfilter/nf_tables_api.c:9530
KASAN: slab-uaf int nf_tables_trans_destroy_work+0x152b/0x1750 net/netfilter/nf_tables_api.c:9597
Read of size 2 at addr ffff88802b0051c4 by task kworker/1:1/45
[..]
Workqueue: events nf_tables_trans_destroy_work
Call Trace:
 nft_ctx_update include/net/netfilter/nf_tables.h:1831 [inline]
 nft_commit_release net/netfilter/nf_tables_api.c:9530 [inline]
 nf_tables_trans_destroy_work+0x152b/0x1750 net/netfilter/nf_tables_api.c:9597

Problem is that the notifier does a conditional flush, but its possible
that the table-to-be-removed is still referenced by transactions being
processed by the worker, so we need to flush unconditionally.

We could make the flush_work depend on whether we found a table to delete
in nf-next to avoid the flush for most cases.

AFAICS this problem is only exposed in nf-next, with
commit e169285f8c56 ("netfilter: nf_tables: do not store nft_ctx in transaction objects"),
with this commit applied there is an unconditional fetch of
table->family which is whats triggering the above splat.

## References
- https://git.kernel.org/stable/c/09e650c3a3a7d804430260510534ccbf71c75b2e
- https://git.kernel.org/stable/c/3325628cb36b7f216c5716e7b5124d9dc81199e4
- https://git.kernel.org/stable/c/4c06c13317b9a08decedcd7aaf706691e336277c
- https://git.kernel.org/stable/c/55a40406aac555defe9bdd0adec9508116ce7cb1
- https://git.kernel.org/stable/c/9f6958ba2e902f9820c594869bd710ba74b7c4c0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42109.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42109
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
