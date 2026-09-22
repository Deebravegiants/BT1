# [H] netfilter: nft_set_pipapo: release elements in clone only from destroy path

## Summary
Severity: High
Advisory: CVE-2024-26809
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26809
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=5.19.0 <6.6.23, >=6.2.0 <6.7.11, >=6.7.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo: release elements in clone only from destroy path

Clone already always provides a current view of the lookup table, use it
to destroy the set, otherwise it is possible to destroy elements twice.

This fix requires:

 212ed75dc5fb ("netfilter: nf_tables: integrate pipapo into commit protocol")

which came after:

 9827a0e6e23b ("netfilter: nft_set_pipapo: release elements in clone from abort path").

## References
- https://git.kernel.org/stable/c/362508506bf545e9ce18c72a2c48dcbfb891ab9c
- https://git.kernel.org/stable/c/5ad233dc731ab64cdc47b84a5c1f78fff6c024af
- https://git.kernel.org/stable/c/821e28d5b506e6a73ccc367ff792bd894050d48b
- https://git.kernel.org/stable/c/9384b4d85c46ce839f51af01374062ce6318b2f2
- https://git.kernel.org/stable/c/b0e256f3dd2ba6532f37c5c22e07cb07a36031ee
- https://git.kernel.org/stable/c/b36b83297ff4910dfc8705402c8abffd4bbf8144
- https://git.kernel.org/stable/c/ff90050771412b91e928093ccd8736ae680063c2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26809.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26809
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
