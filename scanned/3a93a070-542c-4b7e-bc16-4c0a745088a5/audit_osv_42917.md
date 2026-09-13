# [H] dmaengine: dw-edma: Add spinlock to protect DONE_INT_MASK and ABORT_INT_MASK

## Summary
Severity: High
Advisory: CVE-2026-72148
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72148
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: dw-edma: Add spinlock to protect DONE_INT_MASK and ABORT_INT_MASK

The DONE_INT_MASK and ABORT_INT_MASK registers are shared by all DMA
channels, and modifying them requires a read-modify-write sequence.
Because this operation is not atomic, concurrent calls to
dw_edma_v0_core_start() can introduce race conditions if two channels
update these registers simultaneously.

Add a spinlock to serialize access to these registers and prevent race
conditions.

[den: update dw_edma.lock comment]

## References
- https://git.kernel.org/stable/c/1553ca96e9df158d8f37137cf4bf5fb0dc981d94
- https://git.kernel.org/stable/c/21a9834f56d6249aaa6ca7c2d8c182d66c48c3e1
- https://git.kernel.org/stable/c/2247cc25a91fb1b5b86586ed55fdd5b725a7477c
- https://git.kernel.org/stable/c/3989b4775bc2cdbdb4ddc4b1d2420a82b40913f2
- https://git.kernel.org/stable/c/3ee0f478bb29b4ee892b178179a9a76ddd194149
- https://git.kernel.org/stable/c/8ffba0171c6bbce5f093c6dba5a02c0805b31203
- https://git.kernel.org/stable/c/ddbc4a8a4fe296f1fa2e59f7d176fc7c773df640
- https://git.kernel.org/stable/c/f60c7463d44fbc1585d247d0bd6976f7a1099472
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72148.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72148
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
