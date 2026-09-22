# [H] crypto: omap - Allocate OMAP_CRYPTO_FORCE_COPY scatterlists correctly

## Summary
Severity: High
Advisory: CVE-2026-23222
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23222
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.251, >=5.11.0 <5.15.201, >=5.16.0 <6.1.164, >=6.2.0 <6.6.125, >=6.7.0 <6.12.72, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: omap - Allocate OMAP_CRYPTO_FORCE_COPY scatterlists correctly

The existing allocation of scatterlists in omap_crypto_copy_sg_lists()
was allocating an array of scatterlist pointers, not scatterlist objects,
resulting in a 4x too small allocation.

Use sizeof(*new_sg) to get the correct object size.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/1562b1fb7e17c1b3addb15e125c718b2be7f5512
- https://git.kernel.org/stable/c/2ed27b5a1174351148c3adbfc0cd86d54072ba2e
- https://git.kernel.org/stable/c/31aff96a41ae6f1f1687c065607875a27c364da8
- https://git.kernel.org/stable/c/6edf8df4bd29f7bfd245b67b2c31d905f1cfc14b
- https://git.kernel.org/stable/c/79f95b51d4278044013672c27519ae88d07013d8
- https://git.kernel.org/stable/c/953c81941b0ad373674656b8767c00234ebf17ac
- https://git.kernel.org/stable/c/c184341920ed78b6466360ed7b45b8922586c38f
- https://git.kernel.org/stable/c/d1836c628cb72734eb5f7dfd4c996a9c18bba3ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23222.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23222
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
