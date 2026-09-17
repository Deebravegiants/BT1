# [H] netfilter: nf_tables: add hook transactions for device deletions

## Summary
Severity: High
Advisory: CVE-2026-63858
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63858
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: add hook transactions for device deletions

Restore the flag that indicates that the hook is going away, ie.
NFT_HOOK_REMOVE, but add a new transaction object to track deletion
of hooks without altering the basechain/flowtable hook_list during
the preparation phase.

The existing approach that moves the hook from the basechain/flowtable
hook_list to transaction hook_list breaks netlink dump path readers
of this RCU-protected list.

It should be possible use an array for nft_trans_hook to store the
deleted hooks to compact the representation but I am not expecting
many hook object, specially now that wildcard support for devices
is in place.

Note that the nft_trans_chain_hooks() list contains a list of struct
nft_trans_hook objects for DELCHAIN and DELFLOWTABLE commands, while
this list stores struct nft_hook objects for NEWCHAIN and NEWFLOWTABLE.
Note that new commands can be updated to use nft_trans_hook for
consistency.

This patch also adapts the event notification path to deal with the list
of hook transactions.

## References
- https://git.kernel.org/stable/c/10f79dbd7719d1da9f5884d13060322d8729f091
- https://git.kernel.org/stable/c/4e69bfb32b2db323d9205fdb30e284481b37817c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63858.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63858
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
