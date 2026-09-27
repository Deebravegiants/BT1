# [H] wifi: brcmfmac: make release_scratchbuffers idempotent

## Summary
Severity: High
Advisory: CVE-2026-68192
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68192
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: brcmfmac: make release_scratchbuffers idempotent

brcmf_pcie_release_scratchbuffers() frees the shared.scratch and
shared.ringupd DMA buffers with dma_free_coherent() but does not clear
the pointers afterwards, unlike the sibling release_ringbuffers() which
NULLs commonrings/flowrings/idxbuf on release.

Both the bus_reset .reset callback (brcmf_pcie_reset) and
brcmf_pcie_remove() call release_scratchbuffers.  When reset teardown
has run before removal, remove's own teardown would call
dma_free_coherent() a second time on the already-freed DMA allocation.

NULL the pointers after free, matching release_ringbuffers(), so a later
release observes that the allocation has already been released.  This
patch makes repeated sequential release safe; the reset-work lifetime is
handled separately by the following patch.

This issue was found by an in-house static analysis tool.

## References
- https://git.kernel.org/stable/c/044fca8f45ba9ab6ca526163155234cf88287ff5
- https://git.kernel.org/stable/c/0ca80328df23f851c86866720d4977783c919ee6
- https://git.kernel.org/stable/c/382ee00b2d1e31869ae576a60d3fbe7a2153512f
- https://git.kernel.org/stable/c/538c51e9d124cf656f2dd0c0394a8545efc7102d
- https://git.kernel.org/stable/c/5a045c2f0fbf029873d2295178fa0785ade35af0
- https://git.kernel.org/stable/c/739b686aecdb14a6065300ea53401f043e51fd22
- https://git.kernel.org/stable/c/81c58a206d1deee01f4c29236d4154c0872f2a38
- https://git.kernel.org/stable/c/b7d1d8cb1bdca56aecebacd2896615da0acc126a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68192.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
