# [H] nvme-pci: fix dma_vecs leak on p2p memory

## Summary
Severity: High
Advisory: CVE-2026-64020
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64020
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: fix dma_vecs leak on p2p memory

We don't unmap P2P memory, so we don't need to track it. The dma_vec
allocation was getting leaked on the completion.

## References
- https://git.kernel.org/stable/c/24ea0de233d9ebb5ebd6f6018eaf2084af25e3dd
- https://git.kernel.org/stable/c/85686c72966c5ee637893f124ddb31a1cace7bee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64020.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
