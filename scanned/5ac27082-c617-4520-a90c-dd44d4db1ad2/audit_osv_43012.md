# [C] netfilter: nft_lookup: fix catchall element handling with inverted lookups

## Summary
Severity: Critical
Advisory: CVE-2026-72320
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72320
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_lookup: fix catchall element handling with inverted lookups

nft_lookup_eval() decides whether a lookup matched (`found`) from the
direct set lookup and priv->invert before falling back to the
catchall element used by interval sets (e.g. nft_set_rbtree) for the
open-ended default range. Since `found` is never recomputed after
`ext` is replaced by the catchall lookup, inverted lookups
(NFT_LOOKUP_F_INV, "!= @set") can wrongly match or wrongly skip the
catchall element, producing the wrong verdict. Fold the catchall
lookup into `ext` before computing `found`, matching the order
already used by nft_objref_map_eval().

## References
- https://git.kernel.org/stable/c/0ab8880865f9678eb6174e72c1fc4712e44c745c
- https://git.kernel.org/stable/c/238c612357b5a25f03eacf356f95034f8551f218
- https://git.kernel.org/stable/c/e6107a4c74b54cb33e3bce162a63048ae5a6b198
- https://git.kernel.org/stable/c/ef0c7d4b04a0e6ad175323c24bc84e11470dd79d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72320.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72320
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
