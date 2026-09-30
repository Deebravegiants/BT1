# [M] wifi: mt76: dma: fix memory leak running mt76_dma_tx_cleanup

## Summary
Severity: Medium
Advisory: CVE-2023-53430
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53430
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: dma: fix memory leak running mt76_dma_tx_cleanup

Fix device unregister memory leak and alway cleanup all configured
rx queues in mt76_dma_tx_cleanup routine.

## References
- https://git.kernel.org/stable/c/3f7dda36e0b6dfa2cd26191f754ba061ab8191f2
- https://git.kernel.org/stable/c/604990fee0a6d608a6cca179ae474f2a1c6add8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53430.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53430
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
