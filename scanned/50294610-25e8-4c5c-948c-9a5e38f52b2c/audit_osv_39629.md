# [H] netfilter: nf_tables: use list_del_rcu for netlink hooks

## Summary
Severity: High
Advisory: CVE-2026-46324
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46324
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: use list_del_rcu for netlink hooks

nft_netdev_unregister_hooks and __nft_unregister_flowtable_net_hooks need
to use list_del_rcu(), this list can be walked by concurrent dumpers.

Add a new helper and use it consistently.

## References
- https://git.kernel.org/stable/c/0bd93ce4f3c35e845532184331d7917d7e562c80
- https://git.kernel.org/stable/c/0f33e8ad6ac563ae2233dd7f75884e0ee010521d
- https://git.kernel.org/stable/c/f3224ee463f8f6f6ced7dcdf6081add4f8128527
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46324.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46324
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
