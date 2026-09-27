# [H] spi: amlogic: spifc-a4: Fix DMA mapping error handling

## Summary
Severity: High
Advisory: CVE-2026-43461
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43461
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: amlogic: spifc-a4: Fix DMA mapping error handling

Fix three bugs in aml_sfc_dma_buffer_setup() error paths:
1. Unnecessary goto: When the first DMA mapping (sfc->daddr) fails,
   nothing needs cleanup. Use direct return instead of goto.
2. Double-unmap bug: When info DMA mapping failed, the code would
   unmap sfc->daddr inline, then fall through to out_map_data which
   would unmap it again, causing a double-unmap.
3. Wrong unmap size: The out_map_info label used datalen instead of
   infolen when unmapping sfc->iaddr, which could lead to incorrect
   DMA sync behavior.

## References
- https://git.kernel.org/stable/c/0a83d6c9e149a176340190fa9cbadf2266db4c9a
- https://git.kernel.org/stable/c/b20b437666e1cb26a7c499d1664e8f2a0ac67000
- https://git.kernel.org/stable/c/c0b88f1176074f80140ed77fce909f254b7180ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43461.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
