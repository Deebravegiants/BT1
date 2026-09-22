# [M] netfilter: nf_tables: don't fail inserts if duplicate has expired

## Summary
Severity: Medium
Advisory: CVE-2023-52925
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-05
Source: https://osv.dev/vulnerability/CVE-2023-52925
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.11 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: don't fail inserts if duplicate has expired

nftables selftests fail:
run-tests.sh testcases/sets/0044interval_overlap_0
Expected: 0-2 . 0-3, got:
W: [FAILED]     ./testcases/sets/0044interval_overlap_0: got 1

Insertion must ignore duplicate but expired entries.

Moreover, there is a strange asymmetry in nft_pipapo_activate:

It refetches the current element, whereas the other ->activate callbacks
(bitmap, hash, rhash, rbtree) use elem->priv.
Same for .remove: other set implementations take elem->priv,
nft_pipapo_remove fetches elem->priv, then does a relookup,
remove this.

I suspect this was the reason for the change that prompted the
removal of the expired check in pipapo_get() in the first place,
but skipping exired elements there makes no sense to me, this helper
is used for normal get requests, insertions (duplicate check)
and deactivate callback.

In first two cases expired elements must be skipped.

For ->deactivate(), this gets called for DELSETELEM, so it
seems to me that expired elements should be skipped as well, i.e.
delete request should fail with -ENOENT error.

## References
- https://git.kernel.org/stable/c/156369a702c33ad5434a19c3a689bfb836d4e0b8
- https://git.kernel.org/stable/c/59ee68c437c562170265194a99698c805a686bb3
- https://git.kernel.org/stable/c/7845914f45f066497ac75b30c50dbc735e84e884
- https://git.kernel.org/stable/c/891ca5dfe3b718b441fc786014a7ba8f517da188
- https://git.kernel.org/stable/c/af78b0489e8898a8c9449ffc0fdd2e181916f0d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52925.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
