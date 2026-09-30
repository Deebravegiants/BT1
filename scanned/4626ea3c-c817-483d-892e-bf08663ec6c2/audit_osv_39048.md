# [H] net: spacemit: Fix error handling in emac_tx_mem_map()

## Summary
Severity: High
Advisory: CVE-2026-43462
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43462
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: spacemit: Fix error handling in emac_tx_mem_map()

The DMA mappings were leaked on mapping error. Free them with the
existing emac_free_tx_buf() function.

## References
- https://git.kernel.org/stable/c/86292155bea578ebab0ca3b65d4d87ecd8a0e9ea
- https://git.kernel.org/stable/c/c34ebd7b24ea70be3c6fdb6936f79f593f37df60
- https://git.kernel.org/stable/c/edeaba385318f60ec1b32470da4d5eb800294d16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43462.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43462
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
