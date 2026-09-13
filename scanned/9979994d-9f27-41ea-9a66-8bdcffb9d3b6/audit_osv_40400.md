# [H] RDMA/umem: Fix truncation for block sizes >= 4G

## Summary
Severity: High
Advisory: CVE-2026-53133
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53133
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/umem: Fix truncation for block sizes >= 4G

When the iommu is used the linearization of the mapping can give a single
block that is very large split across multiple SG entries.

When __rdma_block_iter_next() reassembles the split SG entries it is
overflowing the 32 bit stack values and computed the wrong DMA addresses
for blocks after the truncation.

Use the right types to hold DMA addresses.

## References
- https://git.kernel.org/stable/c/15fe76e23615f502d051ef0768f86babaf08746c
- https://git.kernel.org/stable/c/2ff4b7817e5b78070c30f5fb5e678e452a2628b3
- https://git.kernel.org/stable/c/8fe0231adebe086c8a459c790944ac026cd99c6e
- https://git.kernel.org/stable/c/ac1aad8e1281534ce936c250f68084fc79c5469e
- https://git.kernel.org/stable/c/afd35fec9297195b759078745549c2671223f24f
- https://git.kernel.org/stable/c/baf8685bcf56dc1efb44b8f6a57c42516e549068
- https://git.kernel.org/stable/c/cc644d5608e3b0dadc970bd6e6aa26b91ea07d0f
- https://git.kernel.org/stable/c/dee2a49adeeb2a5e16a3fc858fa21b841c519802
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53133.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
