# [H] mmc: atmel-mci: Fix use-after-free in atmci_remove due to race condition

## Summary
Severity: High
Advisory: CVE-2026-80556
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80556
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mmc: atmel-mci: Fix use-after-free in atmci_remove due to race condition

In atmci_probe, &host->bh_work is bound with atmci_work_func, and
atmci_interrupt, atmci_timeout_timer and atmci_dma_complete can all
queue this work on system_bh_wq.

If we remove the module, atmci_remove makes cleanup and the memory
allocated for host with devm_kzalloc() is released after the remove
callback returns, while the work mentioned above may still be pending
or running. The sequence of operations that may lead to a UAF bug is
as follows:

CPU0                                      CPU1

                                          | atmci_interrupt
                                          | queue_work(system_bh_wq,
                                          |            &host->bh_work)
atmci_remove                              |
atmci_cleanup_slot(...)                   |
atmci_writel(host, ATMCI_IDR, ~0UL)       |
timer_delete_sync(&host->timer)           |
dma_release_channel(host->dma.chan)       |
free_irq(platform_get_irq(pdev, 0), host) |
                                          | atmci_work_func
                                          | // use host
// devm resources released after          |
// remove returns, host is freed          |
                                          | // use host (use-after-free)

Fix it by canceling the work after all the sources that can schedule
it (IRQ handler, timeout timer and DMA completion callback) have been
stopped, and before proceeding with the remaining cleanup in
atmci_remove.

## References
- https://git.kernel.org/stable/c/22aecf6c4721727a2f724ca0438bc7d4b609bf3f
- https://git.kernel.org/stable/c/7599a73ff66d195a908f5d88b427933a9fb1c02a
- https://git.kernel.org/stable/c/b5060ff2f5460795a3e9f7cdf5052aa42f96ff81
- https://git.kernel.org/stable/c/c125ee35a49a0518521b52b27631eef061b8719a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80556.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80556
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
