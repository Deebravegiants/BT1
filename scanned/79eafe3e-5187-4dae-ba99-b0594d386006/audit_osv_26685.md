# [H] netfilter: nft_set_rbtree: fix null deref on element insertion

## Summary
Severity: High
Advisory: CVE-2023-53566
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53566
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_rbtree: fix null deref on element insertion

There is no guarantee that rb_prev() will not return NULL in nft_rbtree_gc_elem():

general protection fault, probably for non-canonical address 0xdffffc0000000003: 0000 [#1] PREEMPT SMP KASAN
KASAN: null-ptr-deref in range [0x0000000000000018-0x000000000000001f]
 nft_add_set_elem+0x14b0/0x2990
  nf_tables_newsetelem+0x528/0xb30

Furthermore, there is a possible use-after-free while iterating,
'node' can be free'd so we need to cache the next value to use.

## References
- https://git.kernel.org/stable/c/3fa13203b6d90cc3a33af47b058739f92ab82eef
- https://git.kernel.org/stable/c/61ae320a29b0540c16931816299eb86bf2b66c08
- https://git.kernel.org/stable/c/899aa5638568abf5d69de7a7bb95e4615157375b
- https://git.kernel.org/stable/c/a337706c1fb35aac3f26b48aca80421bdbe1d33a
- https://git.kernel.org/stable/c/a836be60a3aabcedcd9c79f545d409ace1f20ba6
- https://git.kernel.org/stable/c/b76db53ee8802ee5683f8cb401d7e2ec6f9b3d56
- https://git.kernel.org/stable/c/ec5caa765f7f6960011c919c9aeb1467940421f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53566.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53566
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
