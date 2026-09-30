# [H] netfilter: nf_tables: fix use-after-free in nf_tables_addchain()

## Summary
Severity: High
Advisory: CVE-2026-23231
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-23231
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: fix use-after-free in nf_tables_addchain()

nf_tables_addchain() publishes the chain to table->chains via
list_add_tail_rcu() (in nft_chain_add()) before registering hooks.
If nf_tables_register_hook() then fails, the error path calls
nft_chain_del() (list_del_rcu()) followed by nf_tables_chain_destroy()
with no RCU grace period in between.

This creates two use-after-free conditions:

 1) Control-plane: nf_tables_dump_chains() traverses table->chains
    under rcu_read_lock(). A concurrent dump can still be walking
    the chain when the error path frees it.

 2) Packet path: for NFPROTO_INET, nf_register_net_hook() briefly
    installs the IPv4 hook before IPv6 registration fails.  Packets
    entering nft_do_chain() via the transient IPv4 hook can still be
    dereferencing chain->blob_gen_X when the error path frees the
    chain.

Add synchronize_rcu() between nft_chain_del() and the chain destroy
so that all RCU readers -- both dump threads and in-flight packet
evaluation -- have finished before the chain is freed.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/2a6586ecfa4ce1413daaafee250d2590e05f1a33
- https://git.kernel.org/stable/c/2f9a4ffeb763aec822f8ff3d1e82202d27d46d4b
- https://git.kernel.org/stable/c/7017745068a9068904e1e7a1b170a5785647cc81
- https://git.kernel.org/stable/c/71e99ee20fc3f662555118cf1159443250647533
- https://git.kernel.org/stable/c/dbd0af8083dd201f07c49110b2ee93710abdff28
- https://git.kernel.org/stable/c/f3fe58ce37926a10115ede527d59b91bcc05400a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23231.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23231
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
