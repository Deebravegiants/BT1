# [C] netfilter: flowtable: publish GC-visible tuple last

## Summary
Severity: Critical
Advisory: CVE-2026-74746
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74746
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: publish GC-visible tuple last

nf_flow_table_iterate() only treats original-direction tuple nodes as
owning entries. Publishing the original node first lets GC observe and
free a flow while flow_offload_add() is still inserting the reply node.
Publish the reply node first and the original node last so GC never
sees a partially installed flow.

KASAN can trigger slab-use-after-free read and write reports in the
flowtable/rhashtable path (rht_deferred_worker, jhash, flow_offload_del,
flow_offload_lookup, etc.).

## References
- https://git.kernel.org/stable/c/0a00254585827f1695aa2700114af622ea754cfa
- https://git.kernel.org/stable/c/2014ac62df9d45bb9a004a043e85df7be09ed780
- https://git.kernel.org/stable/c/211ee5d998d92a7d548811939c65942d06c146e4
- https://git.kernel.org/stable/c/972fdf7c4f5c282a239c88fea614b056c33dc025
- https://git.kernel.org/stable/c/be345dcbddb4643a54252b954af974b16eda8f91
- https://git.kernel.org/stable/c/d16b71231e65cb05daea2b45701fcf09cef041e7
- https://git.kernel.org/stable/c/d37917e7bebe078f3c17e47fd6fc1c9f6e8497b2
- https://git.kernel.org/stable/c/d9d3050a70efe217e73a0751e55fdae6a7092620
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74746.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74746
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
