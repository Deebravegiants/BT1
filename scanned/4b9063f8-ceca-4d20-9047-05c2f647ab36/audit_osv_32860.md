# [H] netfilter: nft_set_pipapo: prevent overflow in lookup table allocation

## Summary
Severity: High
Advisory: CVE-2025-38162
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38162
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.1.167, >=6.2.0 <6.6.125, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo: prevent overflow in lookup table allocation

When calculating the lookup table size, ensure the following
multiplication does not overflow:

- desc->field_len[] maximum value is U8_MAX multiplied by
  NFT_PIPAPO_GROUPS_PER_BYTE(f) that can be 2, worst case.
- NFT_PIPAPO_BUCKETS(f->bb) is 2^8, worst case.
- sizeof(unsigned long), from sizeof(*f->lt), lt in
  struct nft_pipapo_field.

Then, use check_mul_overflow() to multiply by bucket size and then use
check_add_overflow() to the alignment for avx2 (if needed). Finally, add
lt_size_check_overflow() helper and use it to consolidate this.

While at it, replace leftover allocation using the GFP_KERNEL to
GFP_KERNEL_ACCOUNT for consistency, in pipapo_resize().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/43fe1181f738295624696ae9ff611790edb65b5e
- https://git.kernel.org/stable/c/4c5c6aa9967dbe55bd017bb509885928d0f31206
- https://git.kernel.org/stable/c/91edc076439c9e2f34b176149f1c84a47a8ec32f
- https://git.kernel.org/stable/c/a9e757473561da93c6a4136f0e59aba91ec777fc
- https://git.kernel.org/stable/c/c1360ac8156c0a3f2385baef91d8d26fd9d39701
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38162.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38162
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
