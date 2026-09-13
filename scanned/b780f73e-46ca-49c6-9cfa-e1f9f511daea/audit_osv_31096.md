# [C] netfilter: nf_set_pipapo: fix initial map fill

## Summary
Severity: Critical
Advisory: CVE-2024-57947
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-23
Source: https://osv.dev/vulnerability/CVE-2024-57947
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.247, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_set_pipapo: fix initial map fill

The initial buffer has to be inited to all-ones, but it must restrict
it to the size of the first field, not the total field size.

After each round in the map search step, the result and the fill map
are swapped, so if we have a set where f->bsize of the first element
is smaller than m->bsize_max, those one-bits are leaked into future
rounds result map.

This makes pipapo find an incorrect matching results for sets where
first field size is not the largest.

Followup patch adds a test case to nft_concat_range.sh selftest script.

Thanks to Stefano Brivio for pointing out that we need to zero out
the remainder explicitly, only correcting memset() argument isn't enough.

## References
- https://git.kernel.org/stable/c/69b6a67f7052905e928d75a0c5871de50e686986
- https://git.kernel.org/stable/c/77bf0c4ab928ca4c9a99311f4f70ba0c17fecba9
- https://git.kernel.org/stable/c/791a615b7ad2258c560f91852be54b0480837c93
- https://git.kernel.org/stable/c/8058c88ac0df21239daee54b5934d5c80ca9685f
- https://git.kernel.org/stable/c/957a4d1c4c5849e4515c9fb4db21bf85318103dc
- https://git.kernel.org/stable/c/9625c46ce6fd4f922595a4b32b1de5066d70464f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57947.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
