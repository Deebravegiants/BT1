# [H] tty: serial: fsl_lpuart: fix race on RX DMA shutdown

## Summary
Severity: High
Advisory: CVE-2023-53094
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53094
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.10.177, >=5.11.0 <5.15.105, >=5.16.0 <6.1.23, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: serial: fsl_lpuart: fix race on RX DMA shutdown

From time to time DMA completion can come in the middle of DMA shutdown:

<process ctx>:				<IRQ>:
lpuart32_shutdown()
  lpuart_dma_shutdown()
    del_timer_sync()
					lpuart_dma_rx_complete()
					  lpuart_copy_rx_to_tty()
					    mod_timer()
    lpuart_dma_rx_free()

When the timer fires a bit later, sport->dma_rx_desc is NULL:

Unable to handle kernel NULL pointer dereference at virtual address 0000000000000004
pc : lpuart_copy_rx_to_tty+0xcc/0x5bc
lr : lpuart_timer_func+0x1c/0x2c
Call trace:
 lpuart_copy_rx_to_tty
 lpuart_timer_func
 call_timer_fn
 __run_timers.part.0
 run_timer_softirq
 __do_softirq
 __irq_exit_rcu
 irq_exit
 handle_domain_irq
 gic_handle_irq
 call_on_irq_stack
 do_interrupt_handler
 ...

To fix this fold del_timer_sync() into lpuart_dma_rx_free() after
dmaengine_terminate_sync() to make sure timer will not be re-started in
lpuart_copy_rx_to_tty() <= lpuart_dma_rx_complete().

## References
- https://git.kernel.org/stable/c/19a98d56dfedafb25652bdb9cd48a4e73ceba702
- https://git.kernel.org/stable/c/1be6f2b15f902c02e055ae0b419ca789200473c9
- https://git.kernel.org/stable/c/2a36b444cace9580380467fd1183bb5e85bcc80a
- https://git.kernel.org/stable/c/90530e7214c8a04dcdde57502d93fa96af288c38
- https://git.kernel.org/stable/c/954fc9931f0aabf272b5674cf468affdd88d3a36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53094.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53094
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
